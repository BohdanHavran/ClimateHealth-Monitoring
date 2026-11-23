"""Small metadata/aggregate queries only; no training or MySQL access."""
from datetime import datetime, timezone
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]


def get(url, params=None):
    response = requests.get(url, params=params, timeout=(5,20), allow_redirects=False)
    response.raise_for_status()
    return response.json()


def main():
    meta = get('https://data.cdc.gov/api/views/ua7e-t2fy.json')
    endpoint = 'https://data.cdc.gov/resource/ua7e-t2fy.json'
    coverage = get(endpoint, {'$select':'min(weekendingdate) as first_week,max(weekendingdate) as last_week,count(*) as rows,count(distinct jurisdiction) as jurisdictions'})
    jurisdictions = get(endpoint, {'$select':'jurisdiction','$group':'jurisdiction','$limit':100})
    florida = 'FL' if any(row['jurisdiction']=='FL' for row in jurisdictions) else 'Florida'
    target_coverage = get(endpoint, {'$select':'min(weekendingdate) as first_week,max(weekendingdate) as last_week,count(*) as rows',
                                     '$where':f"jurisdiction='{florida}' AND totalconfflunewadm IS NOT NULL"})
    weather = get('https://api.open-meteo.com/v1/forecast', {'latitude':49.84,'longitude':24.03,
                  'current':'temperature_2m,relative_humidity_2m,shortwave_radiation','timezone':'UTC'})
    report = {'checked_at':datetime.now(timezone.utc).isoformat(),
              'cdc':{'dataset_id':'ua7e-t2fy','name':meta.get('name'),'license_id':meta.get('licenseId'),
                     'license':meta.get('license'),'coverage':coverage,'jurisdictions':[r['jurisdiction'] for r in jurisdictions],
                     'target_candidate':'totalconfflunewadm','candidate_jurisdiction':florida,
                     'target_nonnull_coverage':target_coverage,
                     'fields':[{k:c.get(k) for k in ('fieldName','dataTypeName','description')} for c in meta.get('columns',[]) if c.get('fieldName') in {'weekendingdate','jurisdiction','totalconfflunewadm','totalconfflunewadmhosprep','totalconfflunewadmperchosprep'}],
                     'record_level_available_at_verified':False},
              'open_meteo':{'current_units':weather.get('current_units'),
                            'current_fields':list(weather.get('current',{})),
                            'licence_url':'https://open-meteo.com/en/licence'},
              'training_performed':False,'medical_rows_downloaded':False}
    (ROOT/'docs/reports/phase3-public-sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'cdc_coverage':coverage,'florida_target_coverage':target_coverage,
                      'weather_units':weather.get('current_units'),'training_performed':False}))


if __name__ == '__main__':
    main()
