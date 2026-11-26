"""Render source inventory plus reviewed annotations into Ukrainian audit references."""
import json
from collections import defaultdict, deque
from pathlib import Path
from terraform_audit_notes import RESOURCE_NOTES, VARIABLE_PURPOSE, DATA_PURPOSE
from audit_terraform import read_inventory

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/terraform"


def code(value):
    return "`" + str(value).replace("|", "&#124;").replace("\n", " ") + "`"


def references(g):
    nodes = {n['id']: n for n in g['nodes']}
    forward, backward = defaultdict(set), defaultdict(set)
    for e in g['edges']:
        if e['relation'] not in ('contains', 'module_source'):
            forward[e['source']].add(e['target'])
            backward[e['target']].add(e['source'])

    def reach(start, table):
        seen = set()
        queue = deque(table[start])
        while queue:
            n = queue.popleft()
            if n in seen:
                continue
            seen.add(n)
            queue.extend(table[n] - seen)
        return sorted(seen)

    def names(ids):
        return '<br>'.join(code(x) for x in sorted(ids)) or 'Немає явних споживачів/посилань.'

    def source(b):
        return f'[код L{b["line"]}](../../infrastructure/terraform/{b["file"]}#L{b["line"]})'

    modules = {b['labels'][0]: b for b in g['blocks'] if b['kind'] == 'module'}
    variable_docs = ["""# Повний довідник Terraform Variables

Джерело — активний root та всі шість child modules, lexical/static аналіз. Root variables задаються через HCP workspace variables/defaults; child variables заповнюють module arguments у main.tf. Child required=true НЕ означає нове required поле HCP UI. Внутрішні name/region/enabled є API модулів, не дублікати UI значень, які треба вводити двічі.

Required нижче означає «немає default»; це не те саме, що non-null або потрібний лише при count>0. Sensitive=true приховує звичайне відображення, але не шифрує самостійно state; тип string не гарантує, що secret не потрапив у Terraform. ARN metadata не є plaintext password. В усіх прикладах AWS identifiers треба брати лише з власних погоджених ресурсів; вигаданих AMI/account/ARN значень немає.

Used in містить прямі source-level consumers. Affects — транзитивний вплив на AWS resource blocks, включно з validations/provider tags; він не означає обовʼязкову зміну кожного ресурсу при кожному значенні. Структурні contains ребра виключені. Повні addresses дозволяють зіставити запис з DOT/RESOURCE аудитом.
"""]
    variables = [b for b in g['blocks'] if b['kind'] == 'variable']
    for scope in sorted({b['scope'] for b in variables}):
        variable_docs.append(f'\n## {scope}\n')
        for b in [v for v in variables if v['scope'] == scope]:
            name = b['labels'][0]
            attrs = b['attrs']
            nid = b['ids'][0]
            desc = VARIABLE_PURPOSE[name]
            usage = forward[nid]
            impact = [x for x in reach(nid, forward) if nodes[x]['kind'] == 'resource' and nodes[x]['address'].startswith('aws_')]
            recommendation = 'Залишити.'
            if name in ('owner', 'aws_account_id') and scope == 'root':
                recommendation = 'Видалити за дозволом користувача; account validation замінити caller identity, Owner tag прибрати.'
            elif not usage:
                recommendation = 'Невикористана. Запропоновано видалити окремо; в межах цього аудиту не прибирати інші API inputs.'
            elif scope != 'root':
                recommendation = 'Залишити як внутрішній module contract; не додавати до HCP UI.'
            example = attrs.get('default')
            if example is None:
                if scope == 'root' and name == 'environment': example = 'dev або production'
                elif scope == 'root' and name == 'aws_region': example = 'us-east-1 — тільки після погодження'
                elif scope == 'root' and name == 'name_suffix': example = 'demo26 — лише приклад suffix, глобальну унікальність перевірити'
                elif attrs.get('sensitive') == 'true': example = 'Згенероване приватне значення; не публікувати і не копіювати з прикладу'
                elif scope != 'root':
                    call = modules[scope.split('.')[1]]
                    example = 'Root передає: ' + call['attrs'].get(name, 'default child')
                else: example = 'Фактичне погоджене значення з HCP/AWS; довільний identifier не підходить'
            variable_docs.extend([f'\n### {scope}.{name}\n', '| Поле | Пояснення |', '|---|---|',
                f'| Variable | {code(name)}; {source(b)} |',
                f'| Type | {code(attrs.get("type"))} |',
                f'| Default | {code(attrs["default"]) if "default" in attrs else "Немає"} |',
                f'| Required | {"Так, без default" if "default" not in attrs else "Ні; conditional preconditions можуть вимагати значення"} |',
                f'| Sensitive | {attrs.get("sensitive", "false")}; metadata ARN не є secret value |',
                f'| Purpose | {desc} |',
                f'| Used in | {names(usage)} |',
                f'| Affects | {names(impact) if impact else "Не має транзитивних AWS consumers; може лише блокувати Plan або бути невикористаною."} |',
                f'| Example | {code(example)} |',
                f'| Recommendation | {recommendation} |'])
    unused = [b['scope']+'.'+b['labels'][0] for b in variables if not forward[b['ids'][0]]]
    variable_docs.append('\n## Невикористані та схожі за назвою\n\n'+names(unused)+'\n\nRoot inputs задаються один раз у HCP, child inputs передає root. deploy_application керує лише API compute/ALB/DNS/CDN API origin; backend_desired_count задає 0 або 1 task, backend_max_instances — стелю ASG 1 або 2. RDS, S3, ECR, CloudFront і журнали зберігаються незалежно. AI inputs відкладені до реальної потреби. [Поточні HCP inputs](../HCP_TERRAFORM.md); [порядок deployment](VARIANT_B_REPORT.md).\n')
    (OUT/'VARIABLES_REFERENCE.md').write_text('\n'.join(variable_docs).rstrip()+'\n',encoding='utf8')

    resource_docs = ["""# Повний аудит resource blocks

У цьому переліку кожен із 55 AWS resource blocks має окрему таблицю. count/for_each instances не обчислено. «Завжди» означає наявність блоку без його count, а не факт існування ресурсу в AWS. Умовність батьківського module також враховано.

Dependencies/consumers витягнуті з traversals/input-output bindings і явних depends_on. provider/variables/locals можуть зʼявлятися як залежності, не лише AWS ресурси. Region/account permissions/API availability і реальний AWS state не перевірялися. Replacement оцінка консервативна: точне replace/update/destroy визначить лише дозволений provider Plan з існуючим state; нижче не вигадано ForceNew schema.

Cost notes — орієнтири us-east-1 зі збереженого кошторису24.11 та переглянутих офіційних цін, не bill prediction. Не підсумовувати повʼязані policy/rule charges удруге. Детальна різниця reserve/реальних ресурсів — [COST_AUDIT](COST_AUDIT.md).
"""]
    for scope in sorted({b['scope'] for b in g['blocks'] if b['kind']=='resource'}):
        resource_docs.append(f'\n## {scope}\n')
        for b in [x for x in g['blocks'] if x['kind']=='resource' and x['scope']==scope]:
            typ, name = b['labels']
            purpose, cost, public, risk = RESOURCE_NOTES[typ]
            nid = b['ids'][0]
            condition = b['attrs'].get('count', b['attrs'].get('for_each', 'Без власного count/for_each'))
            if scope != 'root':
                call = modules[scope.split('.')[1]]
                condition += '; parent module: '+call['attrs'].get('count', 'без count')
            roots = [x for x in reach(nid, backward) if x.startswith('root::var.')]
            resource_docs.extend([f'\n### {scope}.{typ}.{name}\n','| Поле | Пояснення |','|---|---|',
                f'| Type / name / module | {code(typ)} / {code(name)} / {code(scope)}; {source(b)} |',
                f'| Purpose | {purpose} |',
                f'| Depends on | {names(backward[nid])} |',
                f'| Used by | {names(forward[nid])} |',
                f'| Root inputs, transitively | {names(roots)} |',
                f'| Creation / condition | {code(condition)} |',
                f'| Cost | {cost} |',f'| Public / network | {public} |',f'| Security / replacement / deletion | {risk} |'])
    (OUT/'RESOURCES_AUDIT.md').write_text('\n'.join(resource_docs)+'\n',encoding='utf8')
    module_docs=['# Data sources, locals та outputs\n\nУсі допоміжні блоки активного коду. Expressions не виконувалися. Data sources читають AWS тільки під час майбутнього погодженого HCP run; зараз виконано лише читання локальних файлів.\n']
    for scope in sorted({n['scope'] for n in g['nodes']}):
        module_docs.append('\n## '+scope+'\n\n| Вид / адреса | Вираз або призначення | Джерело |\n|---|---|---|')
        for n in g['nodes']:
            if n['scope']!=scope or n['kind'] not in ('data','local','output'):continue
            if n['kind']=='data':desc=DATA_PURPOSE[n['address'].split('.')[1]]
            else:desc=code(n.get('attrs',{}).get('value',''))
            module_docs.append(f'| {n["kind"]}: {code(n["address"])} | {desc} | {source(n)} |')
    (OUT/'MODULES_REFERENCE.md').write_text('\n'.join(module_docs)+'\n',encoding='utf8')


if __name__ == '__main__':
    graph=read_inventory(OUT/'terraform-inventory.json')
    references(graph)
    print('Wrote complete resource, variable and auxiliary references.')
