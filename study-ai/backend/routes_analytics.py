"""StudyAI — Analytics routes: overview, gaps, and activity heatmap."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_current_user
from database import Concept, LearningEvent, StudyMaterial, User, get_db
from db_utils import get_analytics_overview

router = APIRouter(tags=["analytics"])


@router.get("/analytics/overview")
async def analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate stats: materials, concepts, quizzes, avg score, mastery, streak."""
    data = get_analytics_overview(db, current_user.id)
    return {"success": True, "data": data, "error": None}


@router.get("/analytics/gaps")
async def knowledge_gaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return concepts where mastery < 0.5, grouped by material,
    with an action recommendation.
    """
    weak_concepts = (
        db.query(Concept)
        .filter(Concept.user_id == current_user.id, Concept.mastery_score < 0.5)
        .order_by(Concept.mastery_score.asc())
        .all()
    )

    def action(mastery: float) -> str:
        if mastery < 0.2: return "Urgent review needed"
        if mastery < 0.4: return "Review recommended"
        return "Practice more"

    # Group by material
    material_map: dict[str, dict] = {}
    for c in weak_concepts:
        if c.material_id not in material_map:
            mat = db.query(StudyMaterial).filter(StudyMaterial.id == c.material_id).first()
            material_map[c.material_id] = {
                "material_id":   c.material_id,
                "material_name": mat.filename if mat else "Unknown",
                "concepts":      [],
            }
        material_map[c.material_id]["concepts"].append({
            "id":            c.id,
            "name":          c.name,
            "mastery_score": c.mastery_score,
            "action":        action(c.mastery_score),
            "next_review":   c.next_review.isoformat() if c.next_review else None,
        })

    return {"success": True, "data": list(material_map.values()), "error": None}


@router.get("/analytics/heatmap")
async def activity_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return learning activity for the last 30 days.
    Fills in zeros for days with no activity to ensure a smooth graph.
    """
    # 1. Get dates for the last 30 days
    today = datetime.utcnow().date()
    date_list = [today - timedelta(days=i) for i in range(30)]
    date_list.reverse()
    
    heatmap = {d.strftime("%Y-%m-%d"): {"date": d.strftime("%Y-%m-%d"), "count": 0, "types": []} for d in date_list}

    # 2. Fetch events
    since = datetime.combine(date_list[0], datetime.min.time())
    events = (
        db.query(LearningEvent)
        .filter(
            LearningEvent.user_id   == current_user.id,
            LearningEvent.timestamp >= since,
        )
        .all()
    )

    # 3. Aggregate
    for ev in events:
        day = ev.timestamp.strftime("%Y-%m-%d")
        if day in heatmap:
            heatmap[day]["count"] += 1
            if ev.event_type not in heatmap[day]["types"]:
                heatmap[day]["types"].append(ev.event_type)

    return {
        "success": True,
        "data":    list(heatmap.values()),
        "error":   None,
    }
@router.get("/analytics/coverage")
async def concept_coverage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return concept coverage per material and cross-material overlap.
    Used for the 'Concept Coverage Map' and 'Overlap Heatmap'.
    """
    materials = db.query(StudyMaterial).filter(StudyMaterial.user_id == current_user.id).all()
    
    per_material = []
    concept_to_mats = {} # name -> list of mat names
    
    for m in materials:
        concepts = db.query(Concept).filter(Concept.material_id == m.id).all()
        if not concepts:
            continue
            
        avg_mastery = sum(c.mastery_score for c in concepts) / len(concepts)
        per_material.append({
            "id": m.id,
            "filename": m.filename,
            "concept_count": len(concepts),
            "coverage_pct": round(avg_mastery * 100, 1)
        })
        
        for c in concepts:
            name_norm = c.name.strip().title()
            if name_norm not in concept_to_mats:
                concept_to_mats[name_norm] = []
            if m.filename not in concept_to_mats[name_norm]:
                concept_to_mats[name_norm].append(m.filename)

    # Cross-material overlap: concepts appearing in > 1 material
    overlap = []
    for name, mats in concept_to_mats.items():
        if len(mats) > 1:
            overlap.append({
                "concept": name,
                "count": len(mats),
                "materials": mats
            })

    # Topic-level mock grouping logic (using keywords in filenames)
    # In a production app, this would use LLM categorization or clustering
    topics = {
        "AI & Machine Learning": ["ml", "ai ", "ai_", "learning", "data", "agent", "prompt", "llm", "neural", "network", "vision"],
        "Science & Math": ["math", "phys", "chem", "bio", "calc", "stats"],
        "Humanities": ["history", "social", "philosophy", " literature", "politics", " art "],
        "Other": []
    }
    
    topic_coverage = {}
    for t_name in topics:
        topic_coverage[t_name] = {"sum": 0, "count": 0}

    for m in per_material:
        assigned = False
        fn = m["filename"].lower()
        for t_name, keywords in topics.items():
            if any(k in fn for k in keywords):
                topic_coverage[t_name]["sum"] += m["coverage_pct"]
                topic_coverage[t_name]["count"] += 1
                assigned = True
                break
        if not assigned:
            topic_coverage["Other"]["sum"] += m["coverage_pct"]
            topic_coverage["Other"]["count"] += 1

    topic_summary = []
    for t_name, stats in topic_coverage.items():
        if stats["count"] > 0:
            topic_summary.append({
                "topic": t_name,
                "coverage_pct": round(stats["sum"] / stats["count"], 1)
            })

    return {
        "success": True,
        "data": {
            "per_material": per_material,
            "overlap": sorted(overlap, key=lambda x: x["count"], reverse=True)[:10],
            "topics": topic_summary
        },
        "error": None
    }


@router.get("/analytics/overlap")
async def concept_overlap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Find and return concepts that appear in 2+ different materials.
    Used for the 'Concept Overlap Map' bubble chart.
    """
    all_concepts = db.query(Concept).filter(Concept.user_id == current_user.id).all()
    
    # 1. Group by normalized name
    overlap_map = {} # normalized_name -> list of concepts
    for c in all_concepts:
        norm = c.name.strip().lower()
        if norm not in overlap_map:
            overlap_map[norm] = []
        overlap_map[norm].append(c)
        
    overlapping_list = []
    
    # 2. Filter for those in multiple materials
    for name, concept_objs in overlap_map.items():
        mat_ids = {c.material_id for c in concept_objs}
        if len(mat_ids) >= 2:
            mats_detail = []
            total_mastery = 0
            for c in concept_objs:
                mat = db.query(StudyMaterial).filter(StudyMaterial.id == c.material_id).first()
                mats_detail.append({
                    "material_id":   c.material_id,
                    "filename":      mat.filename if mat else "Unknown",
                    "mastery_score": c.mastery_score
                })
                total_mastery += c.mastery_score
            
            overlapping_list.append({
                "concept_name":      concept_objs[0].name, # Use original casing from first found
                "material_count":    len(mat_ids),
                "materials":         mats_detail,
                "avg_mastery":       round(total_mastery / len(concept_objs), 2),
                "total_occurrences": len(concept_objs)
            })
            
    # 3. Sort by material_count DESC
    overlapping_list.sort(key=lambda x: x["material_count"], reverse=True)
    
    return {
        "success": True,
        "data": {
            "overlapping_concepts": overlapping_list,
            "total_overlap_count":  len(overlapping_list),
            "most_connected":       overlapping_list[0]["concept_name"] if overlapping_list else None
        },
        "error": None
    }
