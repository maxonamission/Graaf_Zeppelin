# S12-01 — DAG Engine domein-agnostisch maken

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: HOOG
**Geschatte omvang**: M
**Status:** ✅ Done

## Doel

De `_from_dict_v2()` parser in `dag_engine.py` accepteert nu alleen hardcoded veldnamen
(`bond_influence`, `disciplines`, `level`, etc.) die specifiek zijn voor het KNSB-sportmodel.
Een nieuw domeinmodel (bijv. "vitale vereniging", gezondheidszorg) kan geheel andere veldnamen
bevatten. De engine moet **alle** extra velden dynamisch overnemen.

## Bevindingen

| Locatie | Probleem |
|---------|----------|
| `app/core/dag_engine.py:525-541` | Node-parsing hardcodeert `bond_influence`, `disciplines`, `level`, `status`, `degree`, `in_degree`, `out_degree` |
| `app/core/dag_engine.py:579-602` | Edge-parsing hardcodeert `bond_influence`, `disciplines`, `slider_sensitivity`, `time_lag` |
| `app/core/dag_engine.py:22-35` | `_POLARITY_MAP` en `_STRENGTH_MAP` bevatten uitsluitend Nederlandse termen |

## Acceptatiecriteria

- [ ] Node-parsing: verplichte velden zijn `id`, `label`; optioneel: `definition`, `domain`. Alle overige velden worden als `**extra_attrs` op de node gezet
- [ ] Edge-parsing: verplichte velden zijn `source`, `target`; optioneel: `polarity`/`direction`, `base_weight`/`strength`, `mechanism`. Alle overige velden als `**extra_attrs` op de edge
- [ ] `_POLARITY_MAP` en `_STRENGTH_MAP` ondersteunen zowel Nederlandse als Engelse termen
- [ ] Backward-compatible: het huidige sportdeelname-model laadt identiek als voorheen
- [ ] Nieuwe test: een minimaal testmodel met afwijkende veldnamen laadt correct
- [ ] `find_relevant_factors()` doorzoekt dynamisch alle string-velden (niet alleen `label`, `definition`, `description`, `domain`)
- [ ] Bestaande tests slagen

## Technische aanpak

```python
# Node-parsing: verplicht + dynamisch
REQUIRED_NODE_FIELDS = {"id"}
MAPPED_NODE_FIELDS = {"label", "definition", "domain"}

for node in data["nodes"]:
    node_id = node["id"]
    attrs = {k: v for k, v in node.items() if k != "id"}
    # Backward-compat aliassen
    if "definition" in attrs and "description" not in attrs:
        attrs["description"] = attrs["definition"]
    if "domain" in attrs and "category" not in attrs:
        attrs["category"] = attrs["domain"]
    dag.graph.add_node(node_id, **attrs)
```

## Afhankelijkheden

- Geen (kan onafhankelijk worden opgepakt)

## Herhaalbaar

Bij elke wijziging aan het model-JSON-schema: controleer dat nieuwe velden automatisch worden opgepakt.
