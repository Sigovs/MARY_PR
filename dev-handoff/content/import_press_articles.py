"""Create (or update) the 37 press articles in the Shopify blog "press".

Python 3.8+, standard library only. Uses the GraphQL Admin API.

Before running:
  1. Online Store > Blog posts > Manage blogs: create the blog "Press" (handle: press).
  2. Settings > Apps and sales channels > Develop apps: create an app with the
     Admin API scopes read_content and write_content. Install it and copy the
     Admin API access token.
  3. Optional: Settings > Custom data > Blog posts: add the three definitions
     press.feature, press.issue_date, press.byline (single line text). The
     script tries to create them too; if the token may not, it says so and goes on.

Usage:
  python import_press_articles.py --dry-run                          # check the data, no network
  python import_press_articles.py --shop mary-margrill.myshopify.com  # token from SHOPIFY_ADMIN_TOKEN
  python import_press_articles.py --shop ... --only people-stylewatch-chain-gang   # one article

Re-running is safe: an article whose handle already exists in the blog is
updated, not duplicated. Images are fetched by Shopify from image_url (the
public preview); to use the local files instead, upload them in the admin.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API_VERSION = '2026-01'

METAFIELDS = [  # namespace press, all single line text, all optional
    ('feature', 'Feature', 'The item as captioned, e.g. "StyleWatch: Chain Gang". Shown under the publication on the tile.'),
    ('issue_date', 'Issue date', 'Only when printed on the clipping, as text (e.g. "March 22, 2004", "June 2007"). Blank = no date anywhere.'),
    ('byline', 'Byline', 'Only when printed. Added to the source line on the article page.'),
]


class GqlError(Exception):
    pass


def gql(shop, token, query, variables=None):
    req = urllib.request.Request(
        f'https://{shop}/admin/api/{API_VERSION}/graphql.json',
        data=json.dumps({'query': query, 'variables': variables or {}}).encode('utf8'),
        headers={'Content-Type': 'application/json', 'X-Shopify-Access-Token': token})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out = json.loads(resp.read().decode('utf8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f'HTTP {e.code}: {e.read().decode("utf8", "replace")[:500]}')
        if out.get('errors'):
            if any('THROTTLED' in json.dumps(err) for err in out['errors']) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise GqlError(json.dumps(out['errors'], indent=1))
        return out['data']
    sys.exit('Gave up after retries.')


def article_input(rec, blog_id):
    metafields = [{'namespace': 'press', 'key': k, 'type': 'single_line_text_field', 'value': rec[k]}
                  for k, _, _ in METAFIELDS if rec.get(k)]
    metafields += [
        {'namespace': 'global', 'key': 'title_tag', 'type': 'single_line_text_field', 'value': rec['seo_title']},
        {'namespace': 'global', 'key': 'description_tag', 'type': 'single_line_text_field', 'value': rec['seo_description']},
    ]
    return {
        'blogId': blog_id,
        'title': rec['title'],
        'handle': rec['handle'],
        'author': {'name': 'Mary Margrill'},
        'body': rec['body_html'],
        'isPublished': True,
        'publishDate': rec['publish_date'],
        'templateSuffix': 'press',
        'image': {'url': rec['image_url'], 'altText': rec['image_alt']},
        'metafields': metafields,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shop', help='your-store.myshopify.com')
    ap.add_argument('--token', default=os.environ.get('SHOPIFY_ADMIN_TOKEN'), help='or set SHOPIFY_ADMIN_TOKEN')
    ap.add_argument('--blog', default='press', help='blog handle (default: press)')
    ap.add_argument('--data', default=os.path.join(HERE, 'press_articles.json'))
    ap.add_argument('--only', help='import a single handle')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    recs = json.load(open(a.data, encoding='utf8'))
    if a.only:
        recs = [r for r in recs if r['handle'] == a.only]
        if not recs:
            sys.exit(f'No article with handle {a.only!r}.')
    handles = [r['handle'] for r in recs]
    assert len(handles) == len(set(handles)), 'duplicate handles'
    dates = [r['publish_date'] for r in sorted(recs, key=lambda r: r['order'])]
    assert dates == sorted(dates, reverse=True), 'publish dates must fall in grid order (newest first)'

    if a.dry_run:
        print(f'{len(recs)} articles OK. First payload:')
        print(json.dumps(article_input(recs[0], 'gid://shopify/Blog/0'), indent=1, ensure_ascii=False)[:1500])
        return
    if not a.shop or not a.token:
        sys.exit('Need --shop and a token (--token or SHOPIFY_ADMIN_TOKEN).')

    blogs = gql(a.shop, a.token, '{ blogs(first: 50) { nodes { id handle } } }')['blogs']['nodes']
    blog = next((b for b in blogs if b['handle'] == a.blog), None)
    if not blog:
        sys.exit(f'Blog {a.blog!r} not found. Create it first (Online Store > Blog posts > Manage blogs).')

    # Metafield definitions make the three fields editable in the admin. "Taken" = already there.
    for key, name, desc in METAFIELDS:
        try:
            d = gql(a.shop, a.token, '''mutation($d: MetafieldDefinitionInput!) {
                  metafieldDefinitionCreate(definition: $d) { userErrors { code message } } }''',
                    {'d': {'name': name, 'namespace': 'press', 'key': key, 'description': desc,
                           'type': 'single_line_text_field', 'ownerType': 'ARTICLE'}})
            errs = [e for e in d['metafieldDefinitionCreate']['userErrors'] if e['code'] != 'TAKEN']
            print(f'definition press.{key}:', 'ok' if not errs else errs)
        except GqlError as e:
            print(f'definition press.{key}: not created ({e.args[0][:200]}). Add it in Settings > Custom data.')

    existing, cursor = {}, None
    while True:
        d = gql(a.shop, a.token, '''query($id: ID!, $after: String) { blog(id: $id) {
              articles(first: 100, after: $after) { nodes { id handle } pageInfo { hasNextPage endCursor } } } }''',
                {'id': blog['id'], 'after': cursor})['blog']['articles']
        existing.update({n['handle']: n['id'] for n in d['nodes']})
        if not d['pageInfo']['hasNextPage']:
            break
        cursor = d['pageInfo']['endCursor']

    for rec in recs:
        inp = article_input(rec, blog['id'])
        if rec['handle'] in existing:
            d = gql(a.shop, a.token, '''mutation($id: ID!, $a: ArticleUpdateInput!) {
                  articleUpdate(id: $id, article: $a) { article { handle } userErrors { field message } } }''',
                    {'id': existing[rec['handle']], 'a': inp})['articleUpdate']
            verb = 'updated'
        else:
            d = gql(a.shop, a.token, '''mutation($a: ArticleCreateInput!) {
                  articleCreate(article: $a) { article { handle } userErrors { field message } } }''',
                    {'a': inp})['articleCreate']
            verb = 'created'
        print(f"{rec['order']:>2} {rec['handle']}: {verb if not d['userErrors'] else d['userErrors']}")
        time.sleep(0.5)


if __name__ == '__main__':
    try:
        main()
    except GqlError as e:
        sys.exit('GraphQL errors: ' + e.args[0])
