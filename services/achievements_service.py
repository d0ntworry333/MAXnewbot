"""Формирование отчётов раздела «Достижения»."""

from __future__ import annotations

from dataclasses import dataclass

from repositories import body_weight_repo, exercise_weight_repo, user_repo


@dataclass(frozen=True)
class WeightPoint:
    label: str
    weight: float
    date_str: str


def _format_date(raw: str) -> str:
    if not raw:
        return "—"
    return raw[:10] if len(raw) >= 10 else raw


def _profile_start_date(profile) -> str:
    return _format_date(profile.created_at)


def _build_body_timeline(user_id: int) -> list[WeightPoint]:
    profile = user_repo.get_first_profile(user_id)
    if not profile:
        return []

    points: list[WeightPoint] = [
        WeightPoint(
            label="Старт (анкета)",
            weight=profile.weight,
            date_str=_profile_start_date(profile),
        )
    ]
    for record in body_weight_repo.get_all_body_weights(user_id):
        points.append(
            WeightPoint(
                label="Взвешивание",
                weight=record.weight,
                date_str=_format_date(record.recorded_at),
            )
        )
    return points


def format_body_before_after(user_id: int) -> str:
    points = _build_body_timeline(user_id)
    if not points:
        return "❌ Нет данных. Сначала заполните анкету."

    start = points[0]
    end = points[-1]
    delta = end.weight - start.weight
    sign = "+" if delta > 0 else ""

    lines = [
        "⚖️ Вес тела: до и после",
        "",
        f"📌 До: {start.weight:.1f} кг ({start.date_str})",
        f"📌 После: {end.weight:.1f} кг ({end.date_str})",
        f"📊 Изменение: {sign}{delta:.1f} кг",
    ]
    if len(points) == 1:
        lines.append("")
        lines.append("💡 Взвешиваний во время тренировок пока нет — «после» совпадает со стартом.")
    return "\n".join(lines)


def format_body_changes(user_id: int) -> str:
    points = _build_body_timeline(user_id)
    if not points:
        return "❌ Нет данных. Сначала заполните анкету."

    lines = ["📈 Изменения веса тела", ""]
    prev = points[0].weight
    for i, pt in enumerate(points, start=1):
        if i == 1:
            lines.append(f"{i}. {pt.date_str} — {pt.weight:.1f} кг ({pt.label})")
        else:
            delta = pt.weight - prev
            sign = "+" if delta > 0 else ""
            lines.append(
                f"{i}. {pt.date_str} — {pt.weight:.1f} кг "
                f"({sign}{delta:.1f} кг к предыдущему)"
            )
        prev = pt.weight
    return "\n".join(lines)


def _exercise_averages(user_id: int) -> list[tuple[str, float, int]]:
    """(название, средний вес, кол-во записей) для каждого упражнения."""
    exercises = exercise_weight_repo.get_distinct_exercises(user_id)
    result: list[tuple[str, float, int]] = []
    for ex_id, ex_name in exercises:
        records = exercise_weight_repo.get_weights_for_exercise(user_id, ex_id)
        if not records:
            continue
        avg = sum(r.weight for r in records) / len(records)
        result.append((ex_name, avg, len(records)))
    return result


def format_strength_average(user_id: int) -> str:
    per_ex = _exercise_averages(user_id)
    if not per_ex:
        return "❌ Нет записей силовых весов. Вводите веса после упражнений в тренировках."

    overall = sum(avg for _, avg, _ in per_ex) / len(per_ex)
    lines = [
        "📊 Средний силовой вес",
        "",
        f"Ваш показатель: {overall:.1f} кг",
        "",
        "Что это значит:",
        "• по каждому упражнению считается средний вес из всех ваших записей;",
        "• эти средние складываются и делятся на число упражнений —",
        "  так получается один общий показатель прогресса за цикл.",
        "",
        "Динамику по каждому упражнению смотрите в разделе «По упражнениям».",
    ]
    return "\n".join(lines)


def format_strength_exercises_list(user_id: int) -> str:
    exercises = exercise_weight_repo.get_distinct_exercises(user_id)
    if not exercises:
        return "❌ Нет записей силовых весов."

    lines = [
        "🏋️ Силовой вес по упражнениям",
        "",
        "Выберите упражнение, чтобы увидеть динамику веса:",
        "",
    ]
    for i, (_, name) in enumerate(exercises, start=1):
        lines.append(f"  {i}. {name}")
    return "\n".join(lines)


def get_exercises_for_menu(user_id: int) -> list[tuple[int, str]]:
    return exercise_weight_repo.get_distinct_exercises(user_id)


def format_exercise_history(user_id: int, exercise_id: int) -> str:
    records = exercise_weight_repo.get_weights_for_exercise(user_id, exercise_id)
    if not records:
        return "❌ Нет записей по этому упражнению."

    name = records[0].exercise_name
    lines = [f"📋 {name}", "", "Динамика веса:"]
    prev: float | None = None
    for i, rec in enumerate(records, start=1):
        date_str = _format_date(rec.training_date)
        week_info = f", нед. {rec.week_number}" if rec.week_number else ""
        if prev is None:
            lines.append(f"  {i}. {date_str}{week_info} — {rec.weight:.1f} кг")
        else:
            delta = rec.weight - prev
            sign = "+" if delta > 0 else ""
            lines.append(
                f"  {i}. {date_str}{week_info} — {rec.weight:.1f} кг "
                f"({sign}{delta:.1f} кг)"
            )
        prev = rec.weight

    avg = sum(r.weight for r in records) / len(records)
    lines.extend(["", f"📊 Средний вес: {avg:.1f} кг ({len(records)} записей)"])
    return "\n".join(lines)
