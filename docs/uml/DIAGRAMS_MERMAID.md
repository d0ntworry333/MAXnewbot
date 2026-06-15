# UML (Mermaid) — для превью в Cursor / GitHub

> Если PlantUML недоступен, скопируйте блоки в https://mermaid.live и экспортируйте PNG.

## 1. Use Case (упрощённо)

```mermaid
flowchart LR
  User((Пользователь))
  Sched((APScheduler))

  subgraph Bot["МАКС-бот «Твой тренер»"]
    UC1[Старт / меню]
    UC2[Анкета]
    UC3[Питание / восстановление]
    UC4[Тренировка дня]
    UC5[Техника / веса]
    UC6[Недельные проверки]
  end

  MAX[API МАКС]
  DB[(SQLite)]

  User --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6
  Sched --> UC6
  Bot --> MAX
  Bot --> DB
```

## 2. State Chart — анкета (полная)

```mermaid
stateDiagram-v2
  [*] --> Height: /form
  Height --> Weight
  Weight --> Activity
  Activity --> Gender: кнопка
  Gender --> Age: кнопка
  Age --> Goal
  Goal --> Saved: дефицит/профицит
  Saved --> [*]: users + BMR
```

## 3. Activity — тренировка дня

```mermaid
flowchart TD
  A[Упражнения дня] --> B{Сессия есть?}
  B -->|нет| Z[Создать сессию]
  B -->|да| C[Опрос самочувствия]
  C --> D[Подбор упражнений]
  D --> E{Боль?}
  E -->|да| F[filter_exercises_by_pain]
  E -->|нет| G[Полный список]
  F --> H[Показ списка]
  G --> H
  H --> I[Ввод весов по очереди]
  I --> J[Сохранение exercise_weights]
  J --> K[Завершение тренировки]
  K --> L{3 дня недели?}
  L -->|да| M[check01/02]
  L -->|нет| N[Статус]
  M --> N
```

## 4. Component / Deployment

```mermaid
flowchart TB
  subgraph Client["Пользователь"]
    MAXApp[Клиент МАКС]
  end

  subgraph Cloud["Платформа МАКС"]
    API[MAX API]
  end

  subgraph Host["Хост: локально / Docker"]
    Main[app/main.py]
    subgraph Handlers
      Nav[navigation]
      Form[form]
      Train[training]
    end
    subgraph Services
      US[user_service]
      TS[training_service]
    end
    subgraph Repo
      DBLayer[repositories]
    end
    SQLite[(users.db)]
    Sched[APScheduler]
  end

  MAXApp <--> API
  API <--> Main
  Main --> Handlers --> Services --> Repo --> SQLite
  Sched --> Services
  Sched --> API
```
