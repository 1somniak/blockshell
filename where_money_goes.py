import requests
import datetime
import time
import csv
import argparse
from collections import defaultdict

BASE = 'https://blockstream.info/api'

def get_address_txs(addr):
    """Paginate and return list of tx summaries for address from Blockstream."""
    txs = []
    url = f"{BASE}/address/{addr}/txs"
    last = None
    while True:
        try:
            res = requests.get(url if last is None else url + f"/chain/{last}")
            res.raise_for_status()
            page = res.json()
        except Exception:
            break
        if not page:
            break
        txs.extend(page)
        last = page[-1]['txid']
        if len(page) < 25:
            break
        time.sleep(0.2)
    return txs

def get_tx_detail(txid):
    """Return full tx detail (includes vin.prevout and vout with addresses)."""
    url = f"{BASE}/tx/{txid}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def iso_date_from_unix(ts):
    # use timezone-aware fromtimestamp to avoid deprecation warnings
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date().isoformat()

def incoming_to_address_in_range(addr, date_from, date_to):
    """Find incoming outputs to `addr` whose block_time is within date range.
    Returns list of dicts: txid, block_time, value_btc, payers (list)
    """
    txs = get_address_txs(addr)
    results = []
    for tx in txs:
        status = tx.get('status', {})
        block_time = status.get('block_time')
        if not block_time:
            continue
        d = iso_date_from_unix(block_time)
        if not (date_from <= d <= date_to):
            continue
        txid = tx['txid']
        # fetch detail to know inputs (payers) and exact vouts
        try:
            detail = get_tx_detail(txid)
        except Exception:
            continue
        payers = set()
        for vin in detail.get('vin', []):
            prev = vin.get('prevout')
            if prev:
                addr_in = prev.get('scriptpubkey_address')
                if addr_in:
                    payers.add(addr_in)
        # sum outputs to our address
        value_sats = 0
        for vout in detail.get('vout', []):
            if vout.get('scriptpubkey_address') == addr:
                value_sats += int(vout.get('value', 0))
        results.append({
            'txid': txid,
            'block_time': iso_date_from_unix(block_time),
            'value_btc': value_sats / 1e8,
            'payers': list(payers)
        })
        time.sleep(0.1)
    return results

def outgoing_from_address(addr, limit=100):
    """Find recent txs where addr is in inputs and return destinations.
    This inspects txs appearing on the address page and checks if addr is in vin.prevout.
    """
    txs = get_address_txs(addr)
    dests = defaultdict(float)
    for tx in txs[:limit]:
        txid = tx['txid']
        try:
            detail = get_tx_detail(txid)
        except Exception:
            continue
        is_spend = False
        for vin in detail.get('vin', []):
            prev = vin.get('prevout')
            if prev and prev.get('scriptpubkey_address') == addr:
                is_spend = True
                break
        if not is_spend:
            continue
        for vout in detail.get('vout', []):
            a = vout.get('scriptpubkey_address')
            v = int(vout.get('value', 0)) / 1e8
            if a:
                dests[a] += v
        time.sleep(0.1)
    return dests

def aggregate_for_targets(targets, date_from, date_to):
    all_rows = []
    per_target_total = {}
    payer_summary = defaultdict(float)
    for t in targets:
        incoming = incoming_to_address_in_range(t, date_from, date_to)
        total = sum(r['value_btc'] for r in incoming)
        per_target_total[t] = total
        for r in incoming:
            payers = r.get('payers', [])
            for p in payers:
                payer_summary[p] += r['value_btc'] / max(1, len(payers))
            all_rows.append((t, r['txid'], r['block_time'], r['value_btc'], ';'.join(payers)))
    return all_rows, per_target_total, payer_summary

def write_csv_rows(path, rows, header):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def main():
    parser = argparse.ArgumentParser(description='Collect ransom txs for addresses on a date range')
    parser.add_argument('--targets', help='Comma-separated addresses or path to file with one address per line', default='12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw')
    parser.add_argument('--from', dest='date_from', help='Start date YYYY-MM-DD', default='2017-06-05')
    parser.add_argument('--to', dest='date_to', help='End date YYYY-MM-DD', default='2017-06-05')
    parser.add_argument('--out', help='Output prefix', default='ransom')
    args = parser.parse_args()

    # parse targets
    if '\n' in args.targets or '\r' in args.targets or args.targets.endswith('.txt'):
        try:
            with open(args.targets, 'r') as f:
                targets = [l.strip() for l in f if l.strip()]
        except Exception:
            targets = [args.targets]
    elif ',' in args.targets:
        targets = [a.strip() for a in args.targets.split(',') if a.strip()]
    else:
        targets = [args.targets]

    rows, per_target_total, payer_summary = aggregate_for_targets(targets, args.date_from, args.date_to)

    # write ransom_tx_list.csv
    write_csv_rows(args.out + '_tx_list.csv', rows, ['target','txid','block_time','amount_btc','payer_addresses'])

    # write summary per target
    summary_rows = []
    total_all = 0.0
    for t, tot in per_target_total.items():
        summary_rows.append((t, tot))
        total_all += tot
    write_csv_rows(args.out + '_summary_per_target.csv', summary_rows, ['address','amount_btc'])

    # payer summary
    payer_rows = sorted(payer_summary.items(), key=lambda x: -x[1])
    write_csv_rows(args.out + '_payer_summary.csv', payer_rows, ['payer_address','approx_amount_btc'])

    # outgoing destinations for each target (where money goes)
    dest_rows = []
    for t in targets:
        dests = outgoing_from_address(t, limit=200)
        for a,v in sorted(dests.items(), key=lambda x: -x[1])[:20]:
            dest_rows.append((t,a,v))
    write_csv_rows(args.out + '_destinations.csv', dest_rows, ['source_address','dest_address','amount_btc'])

    # Print short report
    print('=== SUMMARY ===')
    print('Targets analyzed:', targets)
    print('Total received (BTC) per target:')
    for t, tot in per_target_total.items():
        print(' ', t, tot)
    print('Total aggregated BTC received:', total_all)
    print('\nTop payers (approx):')
    for p, v in payer_rows[:20]:
        print(' ', p, v)
    print('\nTop destinations (where money goes):')
    for s, dest, amt in dest_rows[:20]:
        print(' ', s, '->', dest, amt)

if __name__ == '__main__':
    main()