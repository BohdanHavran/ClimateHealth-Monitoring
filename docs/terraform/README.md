# Terraform documentation

Перший контрольований запуск: [FIRST_HCP_PLAN](FIRST_HCP_PLAN.md), [45 очікуваних ресурсних instances](FIRST_PLAN_RESOURCES.md).

Актуальна реалізація: [варіант B](VARIANT_B_REPORT.md), [State evidence](STATE_VERIFICATION.md), [фактична reuse matrix](VARIANT_B_REUSE.md).

- [HCP variables](../HCP_TERRAFORM.md)
- [Architecture](ARCHITECTURE_GRAPH.md), [Terraform DAG](DEPENDENCY_GRAPH.md), [network](NETWORK_GRAPH.md)
- [All variables](VARIABLES_REFERENCE.md), [all resources](RESOURCES_AUDIT.md), [locals/data/outputs](MODULES_REFERENCE.md)
- [Verification](VERIFICATION.md)

REFERENCE_COMPARISON, INDEPENDENT_REVIEW, SIMPLIFICATION_PROPOSAL — збережений незалежний review коду09f2d79 до реалізації B. CONTROLLED_DEPLOYMENT, READINESS_REPORT, REQUIRED_VARIABLES_AUDIT, AUDIT_REPORT та старі graphify JSON описують попередні етапи. Для виконання користуватися поточним runbook/HCP inputs, а не старими gates. Метод нового графа — власний offline lexical/static аналіз, не Graphify/Plan.
