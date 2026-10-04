"""Build the static academic site with Python's standard library."""
from pathlib import Path
from html import escape
from datetime import date, datetime
import json
import re

ROOT = Path(__file__).resolve().parent.parent
def read(name): return (ROOT / 'content' / name).read_text()

papers = json.loads(read('publications.json'))
news = json.loads(read('news.json'))
metrics = json.loads(read('scholar-metrics.json'))
SITE = 'https://mdtariquzzaman.github.io/'
ME = 'Md. Tariquzzaman'
GSC_TOKEN = 'boT_CMjz6ow5mcyZhAbCVE0JK2v9CAJwCu424PfT1U0'
BING_TOKEN = 'E9CE5F8AA8FFFD3C486CAF3DAAAACB56'

# Inline stroke icons (24px grid, currentColor) so actions read at a glance without JavaScript.
# Content files use {{icon:name}}; render() expands the tokens.
ICONS = {
    'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'arrow-left': '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    'external': '<path d="M7 17 17 7M9 7h8v8"/>',
    'download': '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    'scholar': '<path d="M2 9.5 12 4l10 5.5L12 15z"/><path d="M6 12v4.5c3.3 2.3 8.7 2.3 12 0V12M22 9.5V15"/>',
    'github': '<path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/>',
    'paper': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
    'pdf': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M12 11v6M9.5 14.5 12 17l2.5-2.5"/>',
    'code': '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
    'dataset': '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    'video': '<circle cx="12" cy="12" r="9"/><path d="m10 8.5 5.5 3.5-5.5 3.5z" fill="currentColor"/>',
    'copy': '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>',
    'expand': '<path d="M14 4h6v6M10 20H4v-6M20 4l-6.5 6.5M4 20l6.5-6.5"/>',
    'chevron': '<path d="m6 9 6 6 6-6"/>',
    'badge-check': '<path d="m12 2.5 2.4 1.8 3-.1.9 2.9 2.4 1.8-1 2.8 1 2.8-2.4 1.8-.9 2.9-3-.1L12 21.5l-2.4-1.8-3 .1-.9-2.9-2.4-1.8 1-2.8-1-2.8 2.4-1.8.9-2.9 3 .1z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    'overview': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>',
    'arrow-up': '<path d="M12 19V5M6 11l6-6 6 6"/>',
    'quote': '<path d="M16 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/><path d="M5 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z"/>',
    'trending-up': '<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>',
    'bar-chart': '<path d="M6 20v-6M12 20V4M18 20v-9"/>',
    'tv': '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="m8 3 4 3 4-3"/>',
    'monitor': '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    'film': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 4v16M16 4v16M3 9h5M3 15h5M16 9h5M16 15h5"/>',
    'book-open': '<path d="M12 6.5C10 5 7.5 4.5 4 4.5v13c3.5 0 6 .5 8 2 2-1.5 4.5-2 8-2v-13c-3.5 0-6 .5-8 2z"/><path d="M12 6.5v13"/>',
    'football': '<circle cx="12" cy="12" r="9"/><path d="m12 8 3.4 2.5-1.3 4h-4.2l-1.3-4z"/><path d="M12 3v5M3.7 8.5l4.8 2M20.3 8.5l-4.8 2M7.4 17.5l2.5-3M16.6 17.5l-2.5-3"/>',
    'graduation': '<path d="M2.6 9.1 12 5.2l9.4 3.9-9.4 3.9z"/><path d="M6 12.5V16c0 1.7 2.7 3 6 3s6-1.3 6-3v-3.5"/><path d="M22 10v5"/>',
    'flask': '<path d="M10 2v6.5L4.5 18a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 8.5V2"/><path d="M8.5 2h7M7 15h10"/>',
    'blackboard': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M12 16v4M8 20h8"/><path d="m7 8.5 3 2-3 2M12.5 12.5H17"/>',
    'briefcase': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 12.5h18"/>',
    'trophy': '<path d="M6 4h12v5a6 6 0 0 1-12 0z"/><path d="M12 15v6M8 21h8"/><path d="M6 5H4a2 2 0 0 0 2 2M18 5h2a2 2 0 0 1-2 2"/>',
    'presentation': '<rect x="3" y="4" width="18" height="11" rx="2"/><path d="M12 15v5M8 20h8"/>',
    'journal': '<path d="M6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22.5V4.5A2.5 2.5 0 0 1 6.5 2z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20"/>',
    'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.2A6.5 6.5 0 0 1 21.5 20"/>',
    'tag': '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7" cy="7" r="1.2"/>',
    # Filled brand marks (Simple Icons) for the footer identity links.
    'linkedin': '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
    'bluesky': '<path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"/>',
    'x': '<path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>',
    'orcid': '<path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/>',
    'huggingface': '<path d="M1.4446 11.5059c0 1.1021.1673 2.1585.4847 3.1563-.0378-.0028-.0691-.0058-.1058-.0058-.4209 0-.8015.16-1.0704.4512-.3454.3737-.4984.8335-.4316 1.293a1.576 1.576 0 0 0 .2148.5978c-.2319.1864-.4018.4456-.4844.7578-.0646.2448-.131.7543.2149 1.2794a1.4552 1.4552 0 0 0-.0625.1055c-.208.3923-.2207.8372-.0371 1.25.2783.6258.9696 1.1175 2.3126 1.6467.8356.3292 1.5988.5411 1.6056.543 1.1046.2847 2.104.4277 2.969.4277 1.4173 0 2.4754-.3849 3.1525-1.1446 1.538.2651 2.791.1403 3.592.006.6773.7555 1.7332 1.1387 3.1467 1.1387.8649 0 1.8643-.143 2.969-.4278.0068-.0019.77-.2138 1.6056-.543 1.343-.5292 2.0343-1.0208 2.3126-1.6466.1836-.4129.171-.8577-.037-1.25a1.4685 1.4685 0 0 0-.0626-.1056c.346-.525.2795-1.0346.2149-1.2793-.0826-.3122-.2525-.5714-.4844-.7579.11-.1816.1831-.3788.2148-.5977.0669-.4595-.0862-.9193-.4316-1.293-.2688-.2913-.6495-.4513-1.0704-.4513-.0209 0-.0376.0008-.0588.0018.3162-.9966.4846-2.0518.4846-3.1523 0-5.807-4.7362-10.5144-10.5789-10.5144-5.8426 0-10.5788 4.7073-10.5788 10.5144Zm10.5788-9.4831c5.2727 0 9.5476 4.246 9.5476 9.483a9.4201 9.4201 0 0 1-.2696 2.2365c-.0039-.0047-.0079-.011-.0117-.0156-.274-.3255-.6679-.5059-1.1075-.5059-.352 0-.714.1155-1.0763.3438-.2403.1517-.5058.422-.7793.7598-.2534-.3492-.608-.5832-1.0137-.6465a1.5174 1.5174 0 0 0-.2344-.0176c-.9263 0-1.4828.7993-1.6935 1.5177-.1046.2426-.6065 1.3482-1.3614 2.0978-1.1681 1.1601-1.4458 2.3534-.8396 3.6382-.843.1029-1.5836.0927-2.365-.006.5906-1.212.3626-2.4388-.8426-3.6322-.755-.7496-1.2568-1.8552-1.3614-2.0978-.2107-.7184-.7673-1.5177-1.6935-1.5177-.078 0-.1568.0054-.2344.0176-.4057.0633-.7604.2973-1.0137.6465-.2735-.3379-.539-.6081-.7794-.7598-.3622-.2283-.7243-.3438-1.0762-.3438-.4266 0-.8094.171-1.0821.4786a9.4208 9.4208 0 0 1-.2598-2.1936c0-5.237 4.2749-9.483 9.5475-9.483zM8.6443 7.0036c-.4838.0043-.9503.2667-1.1934.7227-.3536.6633-.1006 1.4873.5645 1.84.351.1862.4883-.5261.836-.6485.3107-.1095.841.399 1.0078.086.3536-.6634.1025-1.4874-.5625-1.84a1.3659 1.3659 0 0 0-.6524-.1602Zm6.8403 0c-.2199-.002-.4426.05-.6504.1602-.665.3526-.9181 1.1766-.5645 1.84.1669.313.6971-.1955 1.0079-.086.3476.1224.4867.8347.838.6485.6649-.3527.916-1.1767.5624-1.84-.243-.456-.7096-.7184-1.1934-.7227Zm-9.7565 1.418a.8768.8768 0 0 0-.877.877c0 .4846.3925.877.877.877a.8768.8768 0 0 0 .877-.877.8768.8768 0 0 0-.877-.877zm12.6434 0c-.4845 0-.879.3925-.879.877 0 .4846.3945.877.879.877a.8768.8768 0 0 0 .877-.877.8768.8768 0 0 0-.877-.877zM8.7927 11.459c-.179-.003-.2793.1107-.2793.416 0 .8097.3874 2.125 1.4279 2.924.207-.7123 1.3453-1.2832 1.5079-1.2012.2315.1167.2191.4417.6074.7266.3884-.285.374-.6098.6056-.7266.1627-.082 1.3009.4889 1.5079 1.2012 1.0404-.799 1.4278-2.1144 1.4278-2.924 0-1.2212-1.583.6402-3.5413.6485-1.4686-.0061-2.7266-1.0558-3.2639-1.0645zM4.312 14.4768c.5792.365 1.6964 2.2751 2.1056 3.0177.1371.2488.371.3536.582.3536.4188 0 .7465-.4138.0391-.9395-1.0636-.791-.6914-2.0846-.1836-2.1642a.4302.4302 0 0 1 .0664-.004c.4616 0 .666.7892.666.7892s.5959 1.4898 1.6213 2.508c.942.9356 1.062 1.703.4961 2.6661-.0164-.004-.0159.0236-.1484.2149-.1853.2673-.4322.4688-.7188.6152-.5062.2269-1.1397.2696-1.7833.2696-1.037 0-2.1017-.1824-2.6975-.336-.0293-.0075-3.6505-.9567-3.1916-1.8224.0771-.1454.2033-.2031.3633-.2031.6463 0 1.823.9551 2.3283.9551.113 0 .196-.0865.2285-.2031.2249-.8045-3.2787-1.0522-2.9846-2.1642.0519-.1967.193-.2757.3907-.2754.854 0 2.7704 1.4923 3.172 1.4923.0307 0 .0525-.0085.0645-.0274.2012-.3227.1096-.5865-1.3087-1.4395-1.4182-.8533-2.4315-1.329-1.8653-1.9416.0651-.0707.1574-.1015.2695-.1015.8611.0002 2.8948 1.84 2.8948 1.84s.5487.5683.8809.5683c.0762 0 .1416-.0315.1855-.1054.2355-.3946-2.1858-2.2183-2.3224-2.971-.0926-.51.0641-.7676.3555-.7676-.0006.008.1701-.0285.4942.1759zm16.2257.5918c-.1366.7526-2.5579 2.5764-2.3224 2.9709.044.074.1092.1055.1855.1055.3321 0 .881-.5684.881-.5684s2.0336-1.8397 2.8947-1.84c.1121 0 .2044.0308.2695.1016.5662.6125-.447 1.0882-1.8653 1.9415-1.4183.853-1.51 1.1168-1.3087 1.4396.012.0188.0337.0273.0644.0273.4016 0 2.3181-1.4923 3.1721-1.4923.1977-.0002.3388.0787.3907.2754.294 1.112-3.2095 1.3597-2.9846 2.1642.0325.1166.1156.2032.2285.2032.5054 0 1.682-.9552 2.3283-.9552.16 0 .2862.0577.3633.2032.459.8656-3.1623 1.8149-3.1916 1.8224-.5958.1535-1.6605.336-2.6975.336-.6351 0-1.261-.0409-1.7638-.2599-.2949-.1472-.5488-.3516-.7383-.625-.0411-.0682-.1026-.1476-.1426-.205-.5726-.9679-.455-1.7371.4903-2.676 1.0254-1.0182 1.6212-2.508 1.6212-2.508s.2044-.7891.666-.7891a.4318.4318 0 0 1 .0665.0039c.5078.0796.88 1.3732-.1836 2.1642-.7074.5257-.3797.9395.039.9395.211 0 .445-.1047.5821-.3535.4092-.7426 1.5264-2.6527 2.1056-3.0178.5588-.3524.99-.1816.8497.5918z"/>',
}

FILLED_ICONS = {'linkedin', 'bluesky', 'x', 'orcid', 'huggingface'}

def icon(name, cls='icon'):
    # Brand marks are filled paths; UI icons are stroked on a 24px grid.
    if name in FILLED_ICONS:
        paint = 'fill="currentColor"'
    else:
        paint = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="18" height="18" {paint} '
            f'aria-hidden="true" focusable="false">{ICONS[name]}</svg>')

def expand_icons(html):
    # Direction and external-link marks trail the label; every other icon leads it.
    trailing = {'external', 'arrow-right'}
    return re.sub(r'\{\{icon:([a-z-]+)\}\}',
                  lambda m: icon(m.group(1), 'icon icon-trail' if m.group(1) in trailing else 'icon'), html)

# Paper resource labels map to an icon and a colour cue, so Paper, Code, and Dataset look different.
LINK_KIND = {'Paper': 'paper', 'Code': 'code', 'Dataset': 'dataset', 'Video': 'video'}

def resource_button(label, href):
    kind = LINK_KIND.get(label, 'paper')
    return (f'<a class="btn" data-kind="{kind}" href="{escape(href, quote=True)}">'
            f'{icon(kind)}<span>{escape(label)}</span>{icon("external", "icon icon-trail")}</a>')

def paper_url(p):
    # One Paper button: the publisher record, else arXiv, else the PDF. Readers reach the PDF from there.
    links = {**p.get('links', {}), **p.get('page', {}).get('links', {})}
    return links.get('Paper') or links.get('arXiv') or p.get('pdf')

def award_html(p):
    if not p.get('award'): return ''
    label = escape(p['award'])
    if p.get('award_url'):
        label = f'<a href="{escape(p["award_url"], quote=True)}">{label}{icon("external", "icon icon-trail")}</a>'
    return f'<p class="award">{label}</p>'

def paper_figures(p):
    # Teaser first, then figures in the order the paper data presents them; each file shows once.
    page, found = p.get('page', {}), []
    if page.get('teaser'): found.append(page['teaser'])
    for sec in page.get('sections', []): found += sec.get('figures', [])
    found += [f['figure'] for f in page.get('findings', []) if f.get('figure')]
    seen, figures = set(), []
    for f in found:
        if f['src'] not in seen: seen.add(f['src']); figures.append(f)
    return figures

def figure_carousel(p):
    figures = paper_figures(p)
    if not figures: return ''
    total = len(figures)
    slides = ''
    for n, f in enumerate(figures, 1):
        src = escape(f['src'], quote=True)
        size = f' width="{f["width"]}" height="{f["height"]}"' if f.get('width') else ''
        label = f' role="group" aria-roledescription="slide" aria-label="Figure {n} of {total}"' if total > 1 else ''
        # The image and the caption link open the same file; only the text link is in the tab order.
        slides += (f'<figure class="carousel-slide"{label}><a class="figure-frame" href="{src}" tabindex="-1">'
                   f'<img src="{src}" alt="{escape(f["alt"], quote=True)}"{size} loading="lazy" decoding="async"></a>'
                   f'<figcaption>{escape(f["caption"])} <a class="figure-zoom" href="{src}">View full size{icon("expand", "icon icon-trail")}</a></figcaption></figure>')
    if total == 1:
        return f'<div class="figure-carousel is-single">{slides}</div>'
    dots = ''.join(f'<button class="carousel-dot" type="button" aria-label="Show figure {n}"></button>' for n in range(1, total + 1))
    # Without JavaScript the track still swipes and scrolls sideways; the controls appear with it.
    controls = (f'<div class="carousel-controls" hidden><button class="carousel-step" type="button" data-step="-1" aria-label="Previous figure">{icon("arrow-left")}</button>'
                f'<div class="carousel-dots">{dots}</div><span class="carousel-status" aria-live="polite">1 / {total}</span>'
                f'<button class="carousel-step" type="button" data-step="1" aria-label="Next figure">{icon("arrow-right")}</button></div>')
    return (f'<div class="figure-carousel" role="region" aria-roledescription="carousel" aria-label="Figures from {escape(p["title"], quote=True)}">'
            f'<div class="carousel-track" tabindex="0">{slides}</div>{controls}</div>')

def publication(p, label):
    pid = escape(p['id'])
    authors = ', '.join('<strong>'+escape(a)+'</strong>' if a == ME else escape(a) for a in p['authors'])
    status = f'<p class="pub-status">{escape(p["status"])}</p>' if p.get('status') else ''
    # Areas are quiet metadata: a small tag mark with a dotted list, not chips.
    areas = [escape(area) for area in p.get('areas', [])]
    areas_html = f'<p class="pub-areas">{icon("tag")}<span>{" · ".join(areas)}</span></p>' if areas else ''
    # Accepted work carries a venue badge linking to the official announcement where known;
    # a preprint's venue stays plain and is never called accepted.
    venue_url = p.get('venue_url')
    badge_name = escape(p["venue"])
    if venue_url:
        badge_name = f'<a href="{escape(venue_url, quote=True)}">{badge_name}{icon("external", "icon icon-trail")}</a>'
    venue = (f'<p class="venue">{escape(p["venue"])}</p>' if is_preprint(p) else
             f'<p class="accepted-venue"><span class="accepted-head">{icon("badge-check")}<span class="accepted-label">Accepted</span></span><span class="accepted-name">{badge_name}</span></p>')
    links = {**p.get('links', {}), **p.get('page', {}).get('links', {})}
    paper = paper_url(p)
    title = f'<a href="{escape(paper, quote=True)}">{escape(p["title"])}</a>' if paper else escape(p['title'])

    # Two drawers: the overview (In short, abstract, figures) and the BibTeX. Without JavaScript they are
    # native <details>; with it, the buttons in the link row open them and the summaries hide.
    page = p.get('page', {})
    lead = page.get('tldr') or p.get('summary', '')
    abstract = f'<details class="paper-abstract"><summary>Full abstract</summary><p>{escape(p["abstract"])}</p></details>' if p.get('abstract') else ''
    overview = (f'<details class="pub-drawer" id="{pid}-overview"><summary>Overview &amp; figures</summary><div class="pub-drawer-body">'
                f'<div class="paper-tldr"><p class="paper-tldr-label">In short</p><p>{escape(lead)}</p>{abstract}</div>{figure_carousel(p)}</div></details>') if lead else ''
    bibtex = '\n'.join(line.rstrip() for line in p.get('bibtex', '').strip().splitlines())
    cite = (f'<details class="pub-drawer pub-cite" id="{pid}-cite"><summary>BibTeX</summary><div class="pub-drawer-body">'
            f'<pre tabindex="0"><code id="{pid}-bibtex">{escape(bibtex)}</code></pre></div></details>') if p.get('bibtex') else ''
    chevron = icon('chevron', 'icon icon-trail icon-chevron')
    buttons = ''
    if overview:
        buttons += (f'<button class="btn drawer-toggle" data-kind="overview" type="button" aria-expanded="false" aria-controls="{pid}-overview" hidden>'
                    f'{icon("overview")}<span>Overview</span>{chevron}</button>')
    if paper: buttons += resource_button('Paper', paper)
    if cite:
        buttons += (f'<span class="btn-split" hidden><button class="btn copy-citation" data-kind="copy" type="button" data-copy-target="{pid}-bibtex">'
                    f'{icon("copy")}<span class="copy-label">Copy BibTeX</span></button>'
                    f'<button class="btn drawer-toggle" data-kind="copy" type="button" aria-expanded="false" aria-controls="{pid}-cite" aria-label="Show BibTeX">{chevron}</button></span>')
    buttons += ''.join(resource_button(label, links[label]) for label in ('Video', 'Dataset', 'Code') if links.get(label))
    return (f'<article class="publication" id="{pid}"><div class="pub-year">{escape(label)}</div><div class="pub-main">{status}<h3>{title}</h3>'
            f'<p class="authors">{authors}</p>{venue}{award_html(p)}{areas_html}'
            f'<div class="link-row paper-links">{buttons}</div>{overview}{cite}</div></article>')

def news_list(items):
    return '<dl class="news">'+''.join(f'<div><dt>{escape(x["date"])}</dt><dd>{x["text"]}</dd></div>' for x in items)+'</dl>'

groups = [('conference', 'conference-papers', 'Conference papers', 'C'),
          ('journal', 'journal-articles', 'Journal articles', 'J'),
          ('workshop', 'workshop-papers', 'Workshop papers', 'W'),
          ('preprint', 'preprints', 'Preprints', 'P')]
GROUP_ICONS = {'conference': 'presentation', 'journal': 'journal', 'workshop': 'users', 'preprint': 'paper'}
metric_items = [(len(papers), 'Publications', 'paper'), (metrics['citations'], 'Citations', 'quote'),
                (metrics['h_index'], 'h-index', 'trending-up'), (metrics['i10_index'], 'i10-index', 'bar-chart')]
unavailable_metric = '<span aria-label="Unavailable">—</span>'
metric_html = ''.join(f'<div><dt>{icon(kind)}<span>{name}</span></dt><dd>{value if value is not None else unavailable_metric}</dd></div>' for value, name, kind in metric_items)
missing_metrics = [name for value, name, _ in metric_items if value is None]
metric_note = ('Google Scholar metrics refreshed' if metrics.get('source') == 'google-scholar' else 'Google Scholar metrics supplied by the author')
if metrics.get('verified_on'): metric_note += ' on ' + escape(metrics['verified_on'])
metric_note += '.'
if missing_metrics: metric_note += ' Unavailable: ' + ', '.join(missing_metrics) + '. See Google Scholar for the latest counts.'

def is_preprint(p):
    # arXiv-only work is a preprint: never label it accepted, on a paper page or in the news.
    return p['type'] == 'preprint' or 'arxiv' in p['venue'].lower()

# Home's Recent list shows every news.json entry, newest first, whatever order the file is in.
for item in news:
    for p in papers:
        if is_preprint(p) and f'publications.html#{p["id"]}"' in item['text'] and 'accept' in item['text'].lower():
            raise SystemExit(f'news.json calls preprint "{p["id"]}" accepted: {item["date"]}')
news_html = news_list(sorted(news, key=lambda x: datetime.strptime(x['date'], '%b %Y'), reverse=True))
contents = ''.join(f'<a href="#{anchor}">{icon(GROUP_ICONS[kind])}<span>{escape(heading)}</span></a>' for kind, anchor, heading, _ in groups)
# Home's interest cards link to the four research-area anchors. Entries are grouped by type,
# so each area anchor is placed before the first paper carrying it, in render order.
AREA_ANCHORS = ['misinformation', 'evaluation', 'bangla', 'accessibility']
AREA_ANCHOR_FOR = {'Misinformation': 'misinformation', 'LLM evaluation': 'evaluation',
                   'Bangla NLP': 'bangla', 'Accessibility': 'accessibility'}
ordered = [p for kind, _, _, _ in groups
           for p in sorted((x for x in papers if x['type'] == kind), key=lambda x: int(x['year']), reverse=True)]
first_anchor = {}
for p in ordered:
    for area in p.get('areas', []):
        key = AREA_ANCHOR_FOR.get(area)
        if key and key not in first_anchor:
            first_anchor[key] = p['id']

def area_anchors(p):
    return ''.join(f'<span id="{key}" class="legacy-anchor"></span>'
                   for key in AREA_ANCHORS if first_anchor.get(key) == p['id'])

sections = ''
for kind, anchor, heading, prefix in groups:
    entries = sorted((p for p in papers if p['type'] == kind), key=lambda p: int(p['year']), reverse=True)
    listing = ''.join(area_anchors(p) + publication(p, f'{prefix}{len(entries)-i}') for i, p in enumerate(entries))
    if not entries: listing = '<p class="empty-publications">No journal articles listed yet.</p>'
    legacy_anchor = '<span id="peer-reviewed" class="legacy-anchor"></span>' if kind == 'conference' else ''
    sections += f'{legacy_anchor}<section class="publication-group" id="{anchor}" aria-labelledby="{anchor}-heading"><h2 id="{anchor}-heading">{escape(heading)} <span class="group-count">{len(entries)}</span></h2>{listing}</section>'
pub_body = f'''<header class="page-heading publications-heading"><p class="eyebrow">Research output</p><h1>Publications</h1><p class="lead">A record of my research, in print and in progress.</p></header>
<div class="publications-summary"><dl class="publication-metrics">{metric_html}</dl><div class="publication-actions"><a class="btn" data-kind="scholar" href="https://scholar.google.com/citations?user=LWB_NzwAAAAJ">{icon("scholar")}<span>Google Scholar</span>{icon("external", "icon icon-trail")}</a><a class="btn" data-kind="cv" href="files/cv/tariq.pdf" target="_blank" rel="noopener">{icon("pdf")}<span>Download CV</span>{icon("external", "icon icon-trail")}</a></div></div><p class="metrics-note">{metric_note}</p>
<div class="reading-layout publications-layout"><nav class="contents page-contents" aria-label="On this page"><p class="eyebrow">On this page</p>{contents}<a href="#resources">{icon("code")}<span>Code &amp; data</span></a></nav><div class="publication-sections">{sections}<section class="section" id="resources"><h2>Code &amp; data</h2><div class="resource-list"><article><h3><a href="https://github.com/lzw108/FMD">{icon("code")}FMD{icon("external", "icon icon-trail")}</a></h3><p>Scenario-induced bias benchmarking for multilingual financial misinformation detection.</p></article><article><h3><a href="https://huggingface.co/datasets/aplycaebous/BdSLIG">{icon("dataset")}BdSLIG{icon("external", "icon icon-trail")}</a></h3><p>Bangla Sign Language instruction generation dataset.</p></article><article><h3><a href="https://github.com/mdtariquzzaman/SPIP">{icon("code")}SPIP{icon("external", "icon icon-trail")}</a></h3><p>Sign Parameter Informed Prompting: reference implementation.</p></article><article><h3><a href="https://github.com/mdtariquzzaman/VITD">{icon("code")}VITD{icon("external", "icon icon-trail")}</a></h3><p>Informal Bangla embeddings and violence-inciting text detection.</p></article></div></section></div></div>'''

personal_data = json.loads(read('personal.json'))
personal_body = read('personal.html')
for category, entries in personal_data.items():
    ranked = category in ('anime', 'movies')
    cards = []
    for index, entry in enumerate(entries, 1):
        title = escape(entry['title']); destination = escape(entry['url'], quote=True)
        if not entry['url'].startswith('https://en.wikipedia.org/wiki/'):
            raise ValueError(f'Personal entry {entry["title"]} must link to Wikipedia')
        author = f'<p class="favorite-author">{escape(entry["author"])}</p>' if entry.get('author') else ''
        cards.append(f'<li class="favorite-card"><a class="favorite-link" href="{destination}"><span class="favorite-order" aria-hidden="true">{index:02}</span><div class="favorite-copy"><h3>{title}</h3>{author}</div><span class="favorite-arrow" aria-hidden="true">{icon("external", "icon icon-trail")}</span></a></li>')
    tag = 'ol' if ranked else 'ul'
    personal_body = personal_body.replace('{{'+category.upper()+'}}', f'<{tag} class="favorites-list favorites-{category}" role="list">'+''.join(cards)+f'</{tag}>')

# Home's Personal teaser: one card per topic, in personal.json order.
TOPIC_LABELS = {'anime': 'Anime', 'movies': 'Movies', 'tv': 'TV shows', 'books': 'Books', 'sports': 'Sports'}
TOPIC_ICONS = {'anime': 'tv', 'movies': 'film', 'tv': 'monitor', 'books': 'book-open', 'sports': 'football'}
personal_topics = '<ul class="topic-grid" role="list">' + ''.join(
    f'<li><a href="personal.html#{c}">{icon(TOPIC_ICONS[c])}<h3>{TOPIC_LABELS[c]}</h3></a></li>' for c in personal_data) + '</ul>'
pages = [('index', 'Home', 'Misinformation detection, LLM evaluation, low-resource Bangla NLP, and sign language accessibility research by Md. Tariquzzaman, Junior Lecturer at IUT.', read('home.html').replace('{{NEWS}}', news_html).replace('{{PERSONAL_TOPICS}}', personal_topics)),
         ('publications', 'Publications', 'Publications, preprints, code, and datasets by Md. Tariquzzaman.', pub_body),
         ('cv', 'CV', 'Education, research publications and experience, teaching experience, industry experience, and awards of Md. Tariquzzaman.', read('cv.html')),
         ('personal', 'Personal', 'Favorite anime, movies, TV shows, books, and sports beyond the academic work of Md. Tariquzzaman.', personal_body)]

PERSON = {'@type': 'Person', '@id': SITE + '#person', 'name': ME,
          'alternateName': ['Tariquzzaman', 'Md Tariquzzaman', 'Tariquzzaman Md'],
          'jobTitle': 'Junior Lecturer', 'url': SITE, 'image': SITE + 'profile.jpg',
          'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Islamic University of Technology', 'url': 'https://www.iutoic-dhaka.edu/'},
          'memberOf': {'@type': 'ResearchOrganization', 'name': 'Systems and Software Lab', 'url': 'https://cse.iutoic-dhaka.edu/ssl'},
          'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'Islamic University of Technology'},
          'knowsAbout': ['Misinformation & harmful content', 'LLM evaluation & bias', 'Low-resource & Bangla NLP', 'Accessibility & sign language'],
          'sameAs': ['https://scholar.google.com/citations?user=LWB_NzwAAAAJ', 'https://github.com/mdtariquzzaman', 'https://www.linkedin.com/in/md-tariquzzaman/', 'https://bsky.app/profile/mdtariquzzaman.bsky.social', 'https://x.com/mdtariquzzaman_', 'https://orcid.org/0009-0002-3322-8741', 'https://huggingface.co/md-tariquzzaman']}

def ld(payload):
    return '<script type="application/ld+json">' + json.dumps(payload, separators=(',', ':')).replace('</', r'<\/') + '</script>'

def arxiv_id(p):
    if p.get('arxiv'): return str(p['arxiv']).removeprefix('arXiv:')
    for value in p.get('links', {}).values():
        match = re.search(r'arxiv\.org/(?:abs|pdf)/([^/?#]+)', value, re.I)
        if match: return match.group(1).removesuffix('.pdf')
    return None

def publication_schema(p):
    url = SITE + 'publications.html#' + p['id']
    item = {'@type': 'ScholarlyArticle', '@id': url, 'name': p['title'], 'headline': p['title'],
            'author': [{'@id': PERSON['@id']} if a == ME else {'@type': 'Person', 'name': a} for a in p['authors']],
            'datePublished': p['year'], 'inLanguage': 'en', 'url': url,
            'creativeWorkStatus': p['status'] or 'Published'}
    if p.get('venue'): item['isPartOf'] = {'@type': 'CreativeWork', 'name': p['venue']}
    if p.get('abstract'): item['abstract'] = p['abstract']
    if p.get('areas'): item['keywords'] = p['areas']
    doi = p.get('doi') or p.get('metadata', {}).get('doi')
    if doi:
        item['identifier'] = {'@type': 'PropertyValue', 'propertyID': 'DOI', 'value': doi, 'url': 'https://doi.org/' + doi}
    aid = arxiv_id(p)
    if aid: item['identifier'] = [{'@type': 'PropertyValue', 'propertyID': 'arXiv', 'value': aid, 'url': f'https://arxiv.org/abs/{aid}'}] + ([item['identifier']] if isinstance(item.get('identifier'), dict) else [])
    if p.get('pdf'):
        pdf = p['pdf'] if p['pdf'].startswith('http') else SITE + p['pdf'].lstrip('/')
        item['encoding'] = {'@type': 'MediaObject', 'contentUrl': pdf, 'encodingFormat': 'application/pdf'}
    item['mainEntityOfPage'] = {'@type': 'WebPage', '@id': SITE + 'publications.html'}
    return item

def render(slug, page_title, description, canonical, body, current=None, head_extra='', noindex=False, asset_prefix=''):
    nav = ''.join(f'<a href="{asset_prefix}{s}.html"' + (' aria-current="page"' if s == current else '') + f'>{t}</a>' for s, t, _, _ in pages)
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow">'
    asset = asset_prefix
    body = expand_icons(body)
    footer_links = [('mail', 'Email', 'mailto:tariquzzaman@iut-dhaka.edu'),
                    ('linkedin', 'LinkedIn', 'https://www.linkedin.com/in/md-tariquzzaman/'),
                    ('bluesky', 'Bluesky', 'https://bsky.app/profile/mdtariquzzaman.bsky.social'),
                    ('x', 'Twitter', 'https://x.com/mdtariquzzaman_'),
                    ('orcid', 'ORCID', 'https://orcid.org/0009-0002-3322-8741'),
                    ('huggingface', 'Hugging Face', 'https://huggingface.co/md-tariquzzaman'),
                    ('arrow-up', 'Back to top', '#main')]
    footer = ''.join(f'<a href="{escape(href, quote=True)}">{icon(name, "icon footer-icon")}<span>{label}</span></a>'
                     for name, label, href in footer_links)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page_title)}</title><meta name="description" content="{escape(description, quote=True)}">{robots}<meta name="google-site-verification" content="{GSC_TOKEN}"><meta name="msvalidate.01" content="{BING_TOKEN}"><meta name="theme-color" content="#fbfbfd" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(page_title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}profile.jpg"><meta property="og:image:alt" content="Md. Tariquzzaman"><meta name="twitter:card" content="summary"><meta name="twitter:site" content="@mdtariquzzaman_"><meta name="twitter:creator" content="@mdtariquzzaman_"><meta name="twitter:title" content="{escape(page_title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SITE}profile.jpg"><link rel="icon" href="{asset}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{asset}assets/style.css?v=20261005f"><link rel="stylesheet" href="{asset}assets/interactions.css?v=20261005f">{head_extra}</head><body class="page-{slug}"><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-inner"><a class="wordmark" href="{asset}index.html" aria-label="Tariq, home">tariq<span>.</span></a><nav aria-label="Main navigation">{nav}</nav><button class="theme-toggle" type="button" aria-label="Switch to dark theme" title="Switch to dark theme"><span aria-hidden="true">◐</span></button></div></header><div class="site-shell"><main id="main">{body}</main><footer class="site-footer"><p>© 2026 Md. Tariquzzaman</p><div>{footer}</div></footer></div><script src="{asset}assets/app.js?v=20261005f"></script></body></html>'''

schemas = {'index': ld({'@context': 'https://schema.org', **PERSON}),
           'publications': ld({'@context': 'https://schema.org', '@graph': [PERSON] + [publication_schema(p) for p in papers]})}
for slug, title, description, body in pages:
    canonical = SITE + ('' if slug == 'index' else slug + '.html')
    page_title = 'Md. Tariquzzaman · Junior Lecturer & NLP Researcher at IUT' if slug == 'index' else title + ' · Md. Tariquzzaman'
    (ROOT / (slug + '.html')).write_text(render(slug, page_title, description, canonical, body, current=slug, head_extra=schemas.get(slug, '')))

# Paper pages were folded into the Publications listing. Old /publications/<id>/ links land on the entry.
for p in papers:
    route = ROOT / 'publications' / p['id'] / 'index.html'; route.parent.mkdir(parents=True, exist_ok=True)
    target = f'../../publications.html#{p["id"]}'
    route.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{escape(p["title"])} · Md. Tariquzzaman</title>'
                     f'<meta name="robots" content="noindex"><link rel="canonical" href="{SITE}publications.html#{p["id"]}">'
                     f'<meta http-equiv="refresh" content="0; url={target}"><script>location.replace("{target}")</script></head>'
                     f'<body><p>This paper is now listed on the <a href="{target}">Publications page</a>.</p></body></html>')

not_found = '<header class="page-heading"><p class="eyebrow">Error 404</p><h1>Page not found</h1><p class="lead">That address does not exist on this site. It may have moved, or the link may be incomplete.</p></header><section class="section"><h2>Try one of these</h2><div class="personal-topics"><a href="index.html">Home{{icon:arrow-right}}</a><a href="publications.html">Publications{{icon:arrow-right}}</a><a href="cv.html">CV{{icon:arrow-right}}</a><a href="personal.html">Personal{{icon:arrow-right}}</a></div></section>'
(ROOT / '404.html').write_text(render('404', 'Page not found · Md. Tariquzzaman', 'That page does not exist on this site.', SITE + '404.html', not_found, noindex=True))

today = date.today().isoformat()
urls = [SITE if s == 'index' else SITE + s + '.html' for s, _, _, _ in pages]
url_xml = ''.join(f'<url><loc>{escape(u)}</loc><lastmod>{today}</lastmod></url>' for u in urls)
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+url_xml+'</urlset>\n')
(ROOT / 'robots.txt').write_text(f'''User-agent: *
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: {SITE}sitemap.xml
''')
llms = '# Md. Tariquzzaman\n\nAcademic website: '+SITE+'\n\nResearch: misinformation and harmful content; LLM evaluation and bias; low-resource and Bangla NLP; accessibility and sign language.\n\n## Profiles\n- [Bluesky](https://bsky.app/profile/mdtariquzzaman.bsky.social)\n- [X](https://x.com/mdtariquzzaman_)\n\n## Pages\n- [Publications]('+SITE+'publications.html)\n- [CV]('+SITE+'cv.html)\n\n## Publications\n' + ''.join(f'- [{p["title"]}]({SITE}publications.html#{p["id"]})\n' for p in papers)
(ROOT / 'llms.txt').write_text(llms)
print(f'Built {len(pages)} static pages, {len(papers)} paper redirects, plus 404.html, sitemap.xml, robots.txt, and llms.txt.')
