from __future__ import annotations

import logging
from datetime import datetime, date, timezone
from typing import Iterable, Optional, Dict, Set

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import UserItemMastery


logger = logging.getLogger(__name__)


def _normalize_session_reference(reference: Optional[str]) -> Optional[str]:
    if reference is None:
        return None
    return reference[:64]


def update_item_mastery(
    user_id: int,
    item_type: str,
    item_id: int,
    is_correct: bool,
    session_reference: Optional[str] = None,
    session_date: Optional[date] = None,
) -> None:
    """
    Update mastery state for a learning item.

    Mastery is achieved after two consecutive correct answers in different sessions (different dates).
    Any incorrect answer resets the streak and mastery status.
    """
    if session_date is None:
        session_date = datetime.now(timezone.utc).date()

    now = datetime.now(timezone.utc)
    session_reference = _normalize_session_reference(
        session_reference or f'{item_type}-{session_date.isoformat()}'
    )

    try:
        mastery = UserItemMastery.query.filter_by(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id
        ).first()

        if mastery is None:
            mastery = UserItemMastery(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                total_attempts=0,
                total_correct=0,
                consecutive_correct_sessions=0,
                last_result=False
            )
            db.session.add(mastery)
            db.session.flush()

        mastery.total_attempts = (mastery.total_attempts or 0) + 1
        mastery.last_attempt_at = now

        if is_correct:
            mastery.total_correct = (mastery.total_correct or 0) + 1

            # Determine if this is a new session (different day or reference)
            is_new_session = (
                mastery.last_session_date is not None
                and mastery.last_session_date != session_date
            )

            if mastery.last_result and is_new_session:
                mastery.consecutive_correct_sessions = (mastery.consecutive_correct_sessions or 0) + 1
            elif mastery.last_result and not is_new_session:
                # Same session, keep at least 1
                mastery.consecutive_correct_sessions = max(mastery.consecutive_correct_sessions or 1, 1)
            else:
                mastery.consecutive_correct_sessions = 1

            mastery.last_correct_at = now

            if mastery.consecutive_correct_sessions >= 2:
                mastery.mastered_at = mastery.mastered_at or now
        else:
            mastery.consecutive_correct_sessions = 0
            mastery.mastered_at = None

        mastery.last_result = is_correct
        mastery.last_session_reference = session_reference
        mastery.last_session_date = session_date
        mastery.updated_at = now
    except SQLAlchemyError as exc:
        logger.error(
            "Failed to update mastery for user=%s item=%s:%s (%s)",
            user_id,
            item_type,
            item_id,
            exc,
            exc_info=True
        )
        db.session.rollback()


def get_mastery_statistics(
    user_id: int,
    item_type: str,
    item_ids: Optional[Iterable[int]] = None,
) -> Dict[str, float]:
    """
    Aggregate mastery statistics for the given user and item type.
    If item_ids provided, restrict stats to that subset.
    """
    try:
        query = UserItemMastery.query.filter_by(user_id=user_id, item_type=item_type)

        item_id_set: Optional[Set[int]] = set(item_ids) if item_ids else None
        if item_id_set:
            if not item_id_set:
                return {
                    'total_items': 0,
                    'mastered_items': 0,
                    'mastered_today': 0,
                    'total_attempts': 0,
                    'total_correct': 0,
                    'accuracy': 0.0,
                }
            query = query.filter(UserItemMastery.item_id.in_(item_id_set))

        total_items = query.count()
        mastered_query = query.filter(UserItemMastery.mastered_at.isnot(None))
        mastered_items = mastered_query.count()

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        mastered_today = mastered_query.filter(UserItemMastery.mastered_at >= today_start).count()

        totals = query.with_entities(
            func.coalesce(func.sum(UserItemMastery.total_correct), 0),
            func.coalesce(func.sum(UserItemMastery.total_attempts), 0),
        ).first()

        total_correct = int(totals[0] or 0)
        total_attempts = int(totals[1] or 0)

        accuracy = 0.0
        if total_attempts > 0:
            accuracy = round((total_correct / total_attempts) * 100, 1)

        return {
            'total_items': total_items,
            'mastered_items': mastered_items,
            'mastered_today': mastered_today,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy': accuracy,
        }
    except SQLAlchemyError as exc:
        logger.error(
            "Failed to gather mastery statistics for user=%s type=%s (%s)",
            user_id,
            item_type,
            exc,
            exc_info=True
        )
        db.session.rollback()
        return {
            'total_items': 0,
            'mastered_items': 0,
            'mastered_today': 0,
            'total_attempts': 0,
            'total_correct': 0,
            'accuracy': 0.0,
        }


