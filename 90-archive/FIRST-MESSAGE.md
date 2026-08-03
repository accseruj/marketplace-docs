---
doc: archived-first-message
purpose: The kickoff prompt for the first Phase -1 session. Retired.
read_when: rarely - reconstructing how Phase -1 was framed before any decision was taken
status: superseded
updated: 2026-08-03
---

ARCHIVED: 2026-08-03. Reason: a one-time kickoff prompt for a session that has since run. Its questions are answered in `00-product/vision.md` section "Launch shape" and in ADR-0006. Superseded by: `00-product/roadmap.md`.

# First message for the new Claude Project chat

Copy everything below the line.

---

Стартуем Phase -1. Контекст в project knowledge — `INDEX.md`, `CONVENTIONS.md`, vision, automation charter, domain model, ADR.

Прочитай `INDEX.md`, `CONVENTIONS.md` и `00-product/automation-charter.md`, затем `60-decisions/ADR-0005-catalog-data-layer.md` и `ADR-0006-product-identity.md` — оба в статусе proposed и блокируют всё остальное.

Мне нужен QA-раунд по реальности поставщиков, чтобы закрыть оба ADR. Задавай по одному-три вопроса за раунд, с конкретными вариантами ответа, и не предполагай за меня. Меня интересуют прежде всего:

1. состав и каналы поставщиков (сколько, API / EDI / SFTP / почта, батч или реалтайм по остаткам)
2. надёжность идентификаторов товара — GTIN / EAN / MPN — и ожидаемое пересечение ассортимента между поставщиками в одной вертикали
3. следствия для стратегии резервирования и риска oversell

По итогам раунда: предложи решение по ADR-0006, затем по ADR-0005, я утверждаю, и ты оформляешь оба ADR в финальном виде плюс правки в `10-architecture/domain-model.md`.

Учти: часть ответов я пока не знаю — там, где я не знаю, скажи, что нужно выяснить у поставщиков и какой вопрос им задать.
