"""Create learning-app tables in supabase via the management API + SQL.

Project ref is taken from SUPABASE_URL; needs SUPABASE_ACCESS_TOKEN env var.
"""
import os, re, json, sys, urllib.request, urllib.error

env = open('/opt/data/learning-app/.env').read()
url = re.search(r'SUPABASE_URL=(\S+)', env).group(1)
ref = re.search(r'ref[=:]?["\s]*(\w{20})', url) or re.search(r'https://(\w{20})\.', url)
ref = re.search(r'https://(\w{20})\.', url).group(1)
tok = os.environ.get('SUPABASE_ACCESS_TOKEN', '').strip()

SQL = r"""
-- learner profiles (was in-memory; now durable)
create table if not exists public.btc_profiles (
  id uuid primary key default gen_random_uuid(),
  answers jsonb not null default '{}'::jsonb,
  grade text,
  tier text,
  created_at timestamptz not null default now()
);
alter table public.btc_profiles enable row level security;
create policy "anyone can insert profiles" on public.btc_profiles for insert to anon with check (true);
create policy "anyone can read profiles" on public.btc_profiles for select to anon using (true);

-- payments: fiat (payfast) + crypto, with sars fields for crypto
create table if not exists public.btc_payments (
  id uuid primary key default gen_random_uuid(),
  method text not null check (method in ('payfast','crypto')),
  tier text,
  amount_zar numeric not null,
  status text not null default 'pending' check (status in ('pending','complete','failed')),
  -- payfast
  pf_payment_id text,
  pf_token text,
  -- crypto / sars
  tx_hash text,
  chain text,
  token text,
  crypto_amount numeric,
  eth_price_usd_at_payment numeric,
  zar_usd_at_payment numeric,
  value_zar_at_payment numeric,
  paid_at timestamptz,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);
alter table public.btc_payments enable row level security;
create policy "anyone can insert payments" on public.btc_payments for insert to anon with check (true);
create policy "anyone can read payments" on public.btc_payments for select to anon using (true);

-- grade-gated question bank keyed by grade band
create table if not exists public.btc_questions (
  id uuid primary key default gen_random_uuid(),
  grade_band text not null check (grade_band in ('foundation','intermediate','senior','fet')),
  subject text not null,
  topic text not null,
  q text not null,
  context text,
  options jsonb not null,
  answer int not null,
  option_notes jsonb,
  rewrites jsonb,
  visual text,
  kinesthetic text,
  intensity text not null default 'standard' check (intensity in ('gentle','standard','stretch')),
  created_at timestamptz not null default now()
);
alter table public.btc_questions enable row level security;
create policy "anyone can read questions" on public.btc_questions for select to anon using (true);
"""

if not tok:
    print('NO_ACCESS_TOKEN')
    sys.exit(0)

api = 'https://api.supabase.com/v1/projects/%s/database/query' % ref
req = urllib.request.Request(api, data=json.dumps({'query': SQL}).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('sql ok:', r.status, r.read().decode()[:400])
except urllib.error.HTTPError as e:
    print('sql failed:', e.code, e.read().decode()[:400])
