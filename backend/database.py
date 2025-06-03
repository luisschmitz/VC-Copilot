from sqlalchemy.orm import Session
from models import StartupAnalysis
from typing import List, Optional


def get_analysis_by_url(db: Session, url: str) -> Optional[StartupAnalysis]:
    """Get a startup analysis by URL"""
    return db.query(StartupAnalysis).filter(StartupAnalysis.url == url).first()


def get_analysis_by_id(db: Session, analysis_id: int) -> Optional[StartupAnalysis]:
    """Get a startup analysis by ID"""
    return db.query(StartupAnalysis).filter(StartupAnalysis.id == analysis_id).first()


def get_all_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[StartupAnalysis]:
    """Get all startup analyses with pagination"""
    return db.query(StartupAnalysis).order_by(StartupAnalysis.created_at.desc()).offset(skip).limit(limit).all()


def create_analysis(db: Session, analysis_data: dict) -> StartupAnalysis:
    """Create a new startup analysis"""
    # Check if analysis for this URL already exists
    existing_analysis = get_analysis_by_url(db, analysis_data["url"])
    
    if existing_analysis:
        # Update existing analysis
        for key, value in analysis_data.items():
            setattr(existing_analysis, key, value)
        db.commit()
        db.refresh(existing_analysis)
        return existing_analysis
    
    # Create new analysis
    db_analysis = StartupAnalysis(**analysis_data)
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def delete_analysis(db: Session, analysis_id: int) -> bool:
    """Delete a startup analysis by ID"""
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        db.delete(analysis)
        db.commit()
        return True
    return False


def search_analyses(db: Session, query: str, limit: int = 10) -> List[StartupAnalysis]:
    """Search for startup analyses by company name or industry"""
    return db.query(StartupAnalysis).filter(
        (StartupAnalysis.company_name.ilike(f"%{query}%")) | 
        (StartupAnalysis.industry.ilike(f"%{query}%"))
    ).limit(limit).all()
