from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_session
from ..db import models
from ..schemas import MetricRead

router = APIRouter()

@router.post('/import')
def trigger_import():
    from ..importer import import_metrics
    import_metrics()
    return {"status": "imported"}

@router.get('/', response_model=list[MetricRead])
def list_metrics(session: Session = Depends(get_session)):
    records = session.query(models.Metric).order_by(models.Metric.date.desc()).all()
    return [MetricRead.from_orm(m) for m in records]

@router.get('/{metric_id}', response_model=MetricRead)
def get_metric(metric_id: int, session: Session = Depends(get_session)):
    metric = session.get(models.Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail='Metric not found')
    return MetricRead.from_orm(metric)
