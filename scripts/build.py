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
ASSET_VERSION = '20261018motion'
SOCIAL_LINKS = (
    ('linkedin', 'LinkedIn', 'https://www.linkedin.com/in/md-tariquzzaman/'),
    ('bluesky', 'Bluesky', 'https://bsky.app/profile/mdtariquzzaman.bsky.social'),
    ('x', 'Twitter', 'https://x.com/mdtariquzzaman_'),
    ('orcid', 'ORCID', 'https://orcid.org/0009-0002-3322-8741'),
    ('huggingface', 'Hugging Face', 'https://huggingface.co/md-tariquzzaman'),
)

# Inline SVG icons on a 24px grid; content tokens expand through render().
# Pixelarticons paths are MIT licensed; see assets/licenses/pixelarticons.txt.
# Content files use {{icon:name}}; render() expands the tokens.
ICONS = {
    'arrow-right': '<path d="M4 11v2h16v-2zm12 2v2h2v-2zm-2 2v2h2v-2zm-2 2v2h2v-2zm4-6V9h2v2z"/><path d="M14 15V7h2v8zm-2 2V5h2v12z"/>',
    'arrow-left': '<path d="M20 11v2H4v-2zM8 13v2H6v-2zm2 2v2H8v-2zm2 2v2h-2v-2zm-4-6V9H6v2z"/><path d="M10 15V7H8v8zm2 2V5h-2v12z"/>',
    'external': '<path d="M11 5H5v2h6V5ZM5 7H3v12h2V7Zm12 12H5v2h12v-2Zm2-6h-2v6h2v-6Zm-8 0H9v2h2v-2Zm2-2h-2v2h2v-2Zm2-2h-2v2h2V9Zm2-2h-2v2h2V7Zm2-2h-2v2h2V5Zm2-2h-2v8h2V3Z"/><path d="M21 3h-8v2h8V3Z"/>',
    'download': '<path d="M21 15v4h-2v-4zm-2 4v2H5v-2zM5 15v4H3v-4zm8-12v14h-2V3z"/><path d="M7 11v2h10v-2zm2 2v2h2v-2zm4 0v2h2v-2z"/><path d="M15 11v2h2v-2z"/>',
    'mail': '<path d="M6 8h2v2H6zm2 2h2v2H8zm10-2h-2v2h2zm-2 2h-2v2h2zm-6 2h4v2h-4zM2 6h2v12H2zm18 0h2v12h-2zM4 4h16v2H4zm0 14h16v2H4z"/>',
    'scholar': '<path d="M2 3h9v2H2zM0 19h11v2H0zM13 3h9v2h-9zm0 16h11v2H13zM11 5h2v18h-2zM0 5h2v14H0zm22 0h2v14h-2zm-7 2h5v2h-5zm0 4h5v2h-5zm0 4h2v2h-2z"/>',
    'github': '<path d="M19 14h-2v2h-2v2h2v4H7v-4H3v-2H1v-2h2v2h4v-2H5v-2H3V6h2V2h4v2h6V2h4v4h2v6h-2v2ZM7 18h2v-2H7v2Z"/>',
    'paper': '<path d="M6 4H4v16h2zm10-2H6v2h10zm4 4h-2v14h2zm-2 14H6v2h12zM16 4h2v2h-2zm-4 0h2v6h-2z"/><path d="M12 8h6v2h-6zm-4 8h8v2H8zm0-4h8v2H8zm0-4h2v2H8z"/>',
    'pdf': '<path d="M21 15v4h-2v-4zm-2 4v2H5v-2zM5 15v4H3v-4zm8-12v14h-2V3z"/><path d="M7 11v2h10v-2zm2 2v2h2v-2zm4 0v2h2v-2z"/><path d="M15 11v2h2v-2z"/>',
    'code': '<path d="M11 18H9v-4h2v4Zm-4-1H5v-2h2v2Zm12-2v2h-2v-2h2ZM5 15H3v-2h2v2Zm16 0h-2v-2h2v2Zm-8-1h-2v-4h2v4ZM3 13H1v-2h2v2Zm20 0h-2v-2h2v2ZM5 11H3V9h2v2Zm16 0h-2V9h2v2Zm-6-1h-2V6h2v4ZM7 9H5V7h2v2Zm12 0h-2V7h2v2Z"/>',
    'dataset': '<path d="M2 6h2v4H2zm0 4h2v4H2zm0 4h2v4H2zm18-8h2v4h-2zm0 4h2v4h-2zm0 4h2v4h-2zM4 4h4v2H4zm0 8h4v-2H4zm0 4h4v-2H4zm0 4h4v-2H4zM16 4h4v2h-4zm0 8h4v-2h-4zm0 4h4v-2h-4zm0 4h4v-2h-4zM8 2h8v2H8zm0 12h8v-2H8zm0 4h8v-2H8zm0 4h8v-2H8z"/>',
    'video': '<path d="M15 11h-2V9h2zm0 4h-2v-2h2zm-2 2h-2v-2h2zm0-8h-2V7h2zm-2-2H9V5h2zM9 21H7V3h2zm6-8h2v-2h-2zm-6 4h2v2H9z"/>',
    'copy': '<path d="M8 6h12v2H8zM4 2h12v2H4zm2 6h2v12H6zM2 4h2v12H2zm6 16h12v2H8zM20 8h2v12h-2zm-4-4h2v2h-2zM4 16h2v2H4z"/>',
    'expand': '<path d="M4 13h16v-2H4zm7-8h2V3h-2zM9 7h4V5H9zm4 0h2V5h-2zm2 2h2V7h-2zM7 9h8V7H7zm4 10h2v2h-2zm-2-2h4v2H9zm4 0h2v2h-2zm2-2h2v2h-2zm-8 0h8v2H7z"/>',
    'chevron': '<path d="M13 16h-2v-2h2v2Zm-2-2H9v-2h2v2Zm4 0h-2v-2h2v2Zm-6-2H7v-2h2v2Zm8 0h-2v-2h2v2ZM7 10H5V8h2v2Zm12 0h-2V8h2v2Z"/>',
    'badge-check': '<path d="M4 2h16v2H4zm0 18h16v2H4zM2 4h2v16H2zm18 0h2v16h-2zM7 12h2v2H7zm2 2h2v2H9zm2-2h2v2h-2zm2-2h2v2h-2zm2-2h2v2h-2z"/>',
    'overview': '<path d="M4 2h16v2H4zm0 18h16v2H4zM2 4h2v16H2zm18 0h2v16h-2zm-4 8h2v2h-2zm-2 2h2v2h-2zm4 0h2v2h-2zm-8 0h2v2h-2zm2 2h2v2h-2zm2 2h2v2h-2z"/><path d="M20 16h2v2h-2zM8 16h2v2H8zm-2 2h2v2H6zM8 6h2v2H8zM6 8h2v2H6zm2 2h2v2H8zm2-2h2v2h-2z"/>',
    'arrow-up': '<path d="M11 20h2V4h-2zm2-12h2V6h-2zm2 2h2V8h-2zm2 2h2v-2h-2zm-6-4H9V6h2z"/><path d="M15 10H7V8h8zm2 2H5v-2h12z"/>',
    'quote': '<path d="M2 8h4v4H2zm6 0h4v4H8zM2 6h2v2H2zm6 0h2v2H8zM4 4h2v2H4zm6 0h2v2h-2zm4 2h8v2h-8zm0 4h8v2h-8zM2 14h20v2H2zm0 4h20v2H2z"/>',
    'trending-up': '<path d="M4 18H2v-2h2v2Zm2-2H4v-2h2v2Zm8 0h-2v-2h2v2Zm-6-2H6v-2h2v2Zm4 0h-2v-2h2v2Zm4 0h-2v-2h2v2Zm6-8v8h-2v-4h-2V8h-4V6h8Zm-12 6H8v-2h2v2Zm8 0h-2v-2h2v2Z"/>',
    'bar-chart': '<path d="M4 2h16v2H4zm0 18h16v2H4zM2 4h2v16H2zm18 0h2v16h-2zM7 11h2v6H7zm4-4h2v10h-2zm4 6h2v4h-2z"/>',
    'tv': '<path d="M4 3h16v2H4zM2 5h2v10H2zm2 10h16v2H4zM20 5h2v10h-2zM6 19h12v2H6zm3-2h2v2H9zm4 0h2v2h-2z"/>',
    'monitor': '<path d="M4 2h16v2H4zm0 14h16v2H4zM2 4h2v12H2zm18 0h2v12h-2zm-9 14h2v2h-2zm-3 2h8v2H8z"/>',
    'film': '<path d="M4 5h4v2H4zm4-2h8v2H8zm8 2h4v2h-4zM2 7h2v12H2zm2 12h16v2H4zM20 7h2v12h-2zM10 8h4v2h-4zm0 6h4v2h-4zm-2-4h2v4H8zm6 0h2v4h-2z"/>',
    'book-open': '<path d="M2 3h9v2H2zM0 19h11v2H0zM13 3h9v2h-9zm0 16h11v2H13zM11 5h2v18h-2zM0 5h2v14H0zm22 0h2v14h-2zm-7 2h5v2h-5zm0 4h5v2h-5zm0 4h2v2h-2z"/>',
    'graduation': '<path d="M2 3h9v2H2zM0 19h11v2H0zM13 3h9v2h-9zm0 16h11v2H13zM11 5h2v18h-2zM0 5h2v14H0zm22 0h2v14h-2zm-7 2h5v2h-5zm0 4h5v2h-5zm0 4h2v2h-2z"/>',
    'blackboard': '<path d="M3 2h4v4H3zM2 8h12v2H2zm7-4h11v2H9zm1 10h10v2H10z"/><path d="M2 9h6v7H2zm0 7h2v4H2zm4 0h2v4H6zM20 6h2v8h-2z"/>',
    'briefcase': '<path d="M2 8h2v12H2zm18 0h2v12h-2zM4 6h16v2H4zm0 14h16v2H4zM8 4h2v2H8zm2-2h4v2h-4zm4 2h2v2h-2z"/>',
    'trophy': '<path d="M16 17H13V19H15V21H9V19H11V17H8V15H16V17ZM18 5H22V11H20V7H18V11H20V13H18V15H16V5H8V15H6V13H4V11H6V7H4V11H2V5H6V3H18V5Z"/>',
    'presentation': '<path d="M1 3h22v2H1zm1 2h2v11H2zm2 11h16v2H4zM20 5h2v11h-2zM9 18h2v2H9zm-2 2h2v2H7zm6-2h2v2h-2zm2 2h2v2h-2z"/>',
    'journal': '<path d="M6 2h14v2H6zm0 18h14v2H6zM20 4h2v16h-2zM4 4h2v16H4z"/><path d="M2 7h6v2H2zm0 4h6v2H2zm0 4h6v2H2zM16 4h2v16h-2z"/>',
    'users': '<path d="M5 2h6v2H5zm10 0h4v2h-4zM5 10h6v2H5zm10 0h4v2h-4zm4-6h2v6h-2zm-8 0h2v6h-2zM3 4h2v6H3zM0 18h2v4H0zm14 0h2v4h-2zm8 0h2v4h-2zM4 14h8v2H4zm12 0h4v2h-4zM2 16h2v2H2zm10 0h2v2h-2zm8 0h2v2h-2z"/>',
    'tag': '<path d="M16 22h-4v-2h4v2Zm-4-2h-2v-2h2v2Zm6 0h-2v-2h2v2Zm-8-2H8v-2h2v2Zm10 0h-2v-2h2v2ZM8 16H6v-2h2v2Zm14 0h-2v-4h2v4ZM6 14H4v-2h2v2Zm-2-2H2V4h2v8Zm16 0h-2v-2h2v2Zm-2-2h-2V8h2v2ZM8 8H6V6h2v2Zm8 0h-2V6h2v2Zm-2-2h-2V4h2v2Zm-2-2H4V2h8v2Z"/>',
    'flask': '<path d="M8 2h8v2h-2v6h2v2h2v4h2v6H4v-6h2v-4h2v-2h2V4H8V2zm4 2v8h-2v2H8v4H6v2h12v-2h-2v-4h-2v-2h-2V4z" fill-rule="evenodd"/>',
    'football': '<path d="M8 2h8v2h4v4h2v8h-2v4h-4v2H8v-2H4v-4H2V8h2V4h4V2zm0 4H6v2H4v8h2v2h2v2h8v-2h2v-2h2V8h-2V6h-2V4H8v2zm2 2h4v2h2v4h-2v2h-4v-2H8v-4h2V8z" fill-rule="evenodd"/>',
    'cursor': '<path d="M6 4h2v2h2v2h2v2h2v2h2v2h-2v2h-2v2h-2v2H8v2H6V4z"/>',
    # The header's motion toggle; play is the same Pixelarticons mark as video.
    'pause': '<path d="M10 20H4V4h6v16Zm8-16v16h-6V4h6Zm-4 2v12h2V6h-2ZM6 18h2V6H6v12Z"/>',
    'play': '<path d="M15 11h-2V9h2zm0 4h-2v-2h2zm-2 2h-2v-2h2zm0-8h-2V7h2zm-2-2H9V5h2zM9 21H7V3h2zm6-8h2v-2h-2zm-6 4h2v2H9z"/>',
    # Filled brand marks (Simple Icons) for the footer identity links.
    'linkedin': '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
    'bluesky': '<path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"/>',
    'x': '<path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>',
    'orcid': '<path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/>',
    'huggingface': '<path d="M1.4446 11.5059c0 1.1021.1673 2.1585.4847 3.1563-.0378-.0028-.0691-.0058-.1058-.0058-.4209 0-.8015.16-1.0704.4512-.3454.3737-.4984.8335-.4316 1.293a1.576 1.576 0 0 0 .2148.5978c-.2319.1864-.4018.4456-.4844.7578-.0646.2448-.131.7543.2149 1.2794a1.4552 1.4552 0 0 0-.0625.1055c-.208.3923-.2207.8372-.0371 1.25.2783.6258.9696 1.1175 2.3126 1.6467.8356.3292 1.5988.5411 1.6056.543 1.1046.2847 2.104.4277 2.969.4277 1.4173 0 2.4754-.3849 3.1525-1.1446 1.538.2651 2.791.1403 3.592.006.6773.7555 1.7332 1.1387 3.1467 1.1387.8649 0 1.8643-.143 2.969-.4278.0068-.0019.77-.2138 1.6056-.543 1.343-.5292 2.0343-1.0208 2.3126-1.6466.1836-.4129.171-.8577-.037-1.25a1.4685 1.4685 0 0 0-.0626-.1056c.346-.525.2795-1.0346.2149-1.2793-.0826-.3122-.2525-.5714-.4844-.7579.11-.1816.1831-.3788.2148-.5977.0669-.4595-.0862-.9193-.4316-1.293-.2688-.2913-.6495-.4513-1.0704-.4513-.0209 0-.0376.0008-.0588.0018.3162-.9966.4846-2.0518.4846-3.1523 0-5.807-4.7362-10.5144-10.5789-10.5144-5.8426 0-10.5788 4.7073-10.5788 10.5144Zm10.5788-9.4831c5.2727 0 9.5476 4.246 9.5476 9.483a9.4201 9.4201 0 0 1-.2696 2.2365c-.0039-.0047-.0079-.011-.0117-.0156-.274-.3255-.6679-.5059-1.1075-.5059-.352 0-.714.1155-1.0763.3438-.2403.1517-.5058.422-.7793.7598-.2534-.3492-.608-.5832-1.0137-.6465a1.5174 1.5174 0 0 0-.2344-.0176c-.9263 0-1.4828.7993-1.6935 1.5177-.1046.2426-.6065 1.3482-1.3614 2.0978-1.1681 1.1601-1.4458 2.3534-.8396 3.6382-.843.1029-1.5836.0927-2.365-.006.5906-1.212.3626-2.4388-.8426-3.6322-.755-.7496-1.2568-1.8552-1.3614-2.0978-.2107-.7184-.7673-1.5177-1.6935-1.5177-.078 0-.1568.0054-.2344.0176-.4057.0633-.7604.2973-1.0137.6465-.2735-.3379-.539-.6081-.7794-.7598-.3622-.2283-.7243-.3438-1.0762-.3438-.4266 0-.8094.171-1.0821.4786a9.4208 9.4208 0 0 1-.2598-2.1936c0-5.237 4.2749-9.483 9.5475-9.483zM8.6443 7.0036c-.4838.0043-.9503.2667-1.1934.7227-.3536.6633-.1006 1.4873.5645 1.84.351.1862.4883-.5261.836-.6485.3107-.1095.841.399 1.0078.086.3536-.6634.1025-1.4874-.5625-1.84a1.3659 1.3659 0 0 0-.6524-.1602Zm6.8403 0c-.2199-.002-.4426.05-.6504.1602-.665.3526-.9181 1.1766-.5645 1.84.1669.313.6971-.1955 1.0079-.086.3476.1224.4867.8347.838.6485.6649-.3527.916-1.1767.5624-1.84-.243-.456-.7096-.7184-1.1934-.7227Zm-9.7565 1.418a.8768.8768 0 0 0-.877.877c0 .4846.3925.877.877.877a.8768.8768 0 0 0 .877-.877.8768.8768 0 0 0-.877-.877zm12.6434 0c-.4845 0-.879.3925-.879.877 0 .4846.3945.877.879.877a.8768.8768 0 0 0 .877-.877.8768.8768 0 0 0-.877-.877zM8.7927 11.459c-.179-.003-.2793.1107-.2793.416 0 .8097.3874 2.125 1.4279 2.924.207-.7123 1.3453-1.2832 1.5079-1.2012.2315.1167.2191.4417.6074.7266.3884-.285.374-.6098.6056-.7266.1627-.082 1.3009.4889 1.5079 1.2012 1.0404-.799 1.4278-2.1144 1.4278-2.924 0-1.2212-1.583.6402-3.5413.6485-1.4686-.0061-2.7266-1.0558-3.2639-1.0645zM4.312 14.4768c.5792.365 1.6964 2.2751 2.1056 3.0177.1371.2488.371.3536.582.3536.4188 0 .7465-.4138.0391-.9395-1.0636-.791-.6914-2.0846-.1836-2.1642a.4302.4302 0 0 1 .0664-.004c.4616 0 .666.7892.666.7892s.5959 1.4898 1.6213 2.508c.942.9356 1.062 1.703.4961 2.6661-.0164-.004-.0159.0236-.1484.2149-.1853.2673-.4322.4688-.7188.6152-.5062.2269-1.1397.2696-1.7833.2696-1.037 0-2.1017-.1824-2.6975-.336-.0293-.0075-3.6505-.9567-3.1916-1.8224.0771-.1454.2033-.2031.3633-.2031.6463 0 1.823.9551 2.3283.9551.113 0 .196-.0865.2285-.2031.2249-.8045-3.2787-1.0522-2.9846-2.1642.0519-.1967.193-.2757.3907-.2754.854 0 2.7704 1.4923 3.172 1.4923.0307 0 .0525-.0085.0645-.0274.2012-.3227.1096-.5865-1.3087-1.4395-1.4182-.8533-2.4315-1.329-1.8653-1.9416.0651-.0707.1574-.1015.2695-.1015.8611.0002 2.8948 1.84 2.8948 1.84s.5487.5683.8809.5683c.0762 0 .1416-.0315.1855-.1054.2355-.3946-2.1858-2.2183-2.3224-2.971-.0926-.51.0641-.7676.3555-.7676-.0006.008.1701-.0285.4942.1759zm16.2257.5918c-.1366.7526-2.5579 2.5764-2.3224 2.9709.044.074.1092.1055.1855.1055.3321 0 .881-.5684.881-.5684s2.0336-1.8397 2.8947-1.84c.1121 0 .2044.0308.2695.1016.5662.6125-.447 1.0882-1.8653 1.9415-1.4183.853-1.51 1.1168-1.3087 1.4396.012.0188.0337.0273.0644.0273.4016 0 2.3181-1.4923 3.1721-1.4923.1977-.0002.3388.0787.3907.2754.294 1.112-3.2095 1.3597-2.9846 2.1642.0325.1166.1156.2032.2285.2032.5054 0 1.682-.9552 2.3283-.9552.16 0 .2862.0577.3633.2032.459.8656-3.1623 1.8149-3.1916 1.8224-.5958.1535-1.6605.336-2.6975.336-.6351 0-1.261-.0409-1.7638-.2599-.2949-.1472-.5488-.3516-.7383-.625-.0411-.0682-.1026-.1476-.1426-.205-.5726-.9679-.455-1.7371.4903-2.676 1.0254-1.0182 1.6212-2.508 1.6212-2.508s.2044-.7891.666-.7891a.4318.4318 0 0 1 .0665.0039c.5078.0796.88 1.3732-.1836 2.1642-.7074.5257-.3797.9395.039.9395.211 0 .445-.1047.5821-.3535.4092-.7426 1.5264-2.6527 2.1056-3.0178.5588-.3524.99-.1816.8497.5918z"/>',
}

BRAND_ICONS = {'linkedin', 'bluesky', 'x', 'orcid', 'huggingface', 'github'}
PIXEL_ICONS = set(ICONS) - BRAND_ICONS
FILLED_ICONS = BRAND_ICONS | PIXEL_ICONS

def icon(name, cls='icon'):
    # Brand marks and pixel UI paths use currentColor with no stroke.
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

# Paper resource labels map to an icon and a colour cue, so Paper, Website, Code, and Dataset look different.
LINK_KIND = {'Paper': 'paper', 'Website': 'monitor', 'Code': 'code', 'Code & Data': 'code', 'Dataset': 'dataset', 'Video': 'video'}

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
    shown_authors = p['authors']
    if len(shown_authors) > 10:
        cutoff = shown_authors.index(ME) + 1 if ME in shown_authors else 1
        shown_authors = shown_authors[:cutoff]
    authors = ', '.join('<strong>'+escape(a)+'</strong>' if a == ME else escape(a) for a in shown_authors)
    if len(shown_authors) < len(p['authors']): authors += ', et al.'
    authors_html = f'<p class="authors">{authors}</p>'
    # The marker and venue convey type/status; retain any distinct supplied status.
    status_text = p.get('status', '')
    repeated_status = {'Conference paper', 'Journal article', 'Workshop paper', 'Preprint', 'Accepted', 'Published'}
    status = f'<p class="pub-status">{escape(status_text)}</p>' if status_text and status_text not in repeated_status else ''
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
    if links.get('Website'): buttons += resource_button('Website', links['Website'])
    if cite:
        buttons += (f'<span class="btn-split" hidden><button class="btn copy-citation" data-kind="copy" type="button" data-copy-target="{pid}-bibtex">'
                    f'{icon("copy")}<span class="copy-label">Copy BibTeX</span></button>'
                    f'<button class="btn drawer-toggle" data-kind="copy" type="button" aria-expanded="false" aria-controls="{pid}-cite" aria-label="Show BibTeX">{chevron}</button></span>')
    buttons += ''.join(resource_button(label, links[label]) for label in ('Video', 'Dataset', 'Code', 'Code & Data') if links.get(label))
    return (f'<article class="publication" id="{pid}"><div class="pub-year">{escape(label)}</div><div class="pub-main">{status}<h3>{title}</h3>'
            f'{authors_html}{venue}{award_html(p)}{areas_html}'
            f'<div class="link-row paper-links">{buttons}</div>{overview}{cite}</div></article>')

def news_list(items):
    return '<dl class="news">'+''.join(f'<div><dt>{escape(x["date"])}</dt><dd>{x["text"]}</dd></div>' for x in items)+'</dl>'

PUBLICATION_TYPES = {'conference': ('C', 'Conference', 'conference-papers'),
                     'journal': ('J', 'Journal', 'journal-articles'),
                     'workshop': ('W', 'Workshop', 'workshop-papers'),
                     'preprint': ('P', 'Preprint', 'preprints')}

def publication_sort_key(p):
    # Use the approved record date when available; year-only records keep that precision.
    if p.get('date'):
        record_date = date.fromisoformat(p['date'])
        if record_date.year != int(p['year']):
            raise ValueError(f'Publication date and year disagree for {p["id"]}')
    return (p.get('date') or p['year'], p.get('arxiv', ''))

ordered = sorted(papers, key=publication_sort_key, reverse=True)
publication_years = list(dict.fromkeys(p['year'] for p in ordered))
remaining = {kind: sum(p['type'] == kind for p in ordered) for kind in PUBLICATION_TYPES}
labels_by_id = {}
for p in ordered:
    labels_by_id[p['id']] = f'{PUBLICATION_TYPES[p["type"]][0]}{remaining[p["type"]]}'
    remaining[p['type']] -= 1
publication_key = '<h2 id="publication-key" class="publication-key">' + ' · '.join(
    f'<span>{prefix}: {label}</span>' for prefix, label, _ in PUBLICATION_TYPES.values()) + '</h2>'
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

# The newest three updates stay visible; every older entry remains in a native disclosure.
for item in news:
    for p in papers:
        if is_preprint(p) and f'publications.html#{p["id"]}"' in item['text'] and 'accept' in item['text'].lower():
            raise SystemExit(f'news.json calls preprint "{p["id"]}" accepted: {item["date"]}')
ordered_news = sorted(news, key=lambda x: datetime.strptime(x['date'], '%b %Y'), reverse=True)
news_html = news_list(ordered_news[:3])
if len(ordered_news) > 3:
    news_html += (f'<details class="news-archive"><summary>Earlier updates '
                  f'<span class="archive-count">({len(ordered_news)-3})</span></summary>'
                  f'{news_list(ordered_news[3:])}</details>')
# Home's interest cards link to the four research-area anchors. Each area anchor is
# placed before the first paper carrying it in the shared chronological catalogue.
# New interest areas get stable anchors as their publication records arrive. Keep the
# older anchors because existing links may still point to the historical topics.
AREA_ANCHOR_FOR = {'LLM safety': 'safety', 'Cultural bias': 'cultural-bias',
                   'AI creativity & storytelling': 'creativity', 'Accessibility': 'accessibility',
                   'Misinformation': 'misinformation', 'LLM evaluation': 'evaluation',
                   'Bangla NLP': 'bangla'}
first_anchor = {}
for p in ordered:
    for area in p.get('areas', []):
        key = AREA_ANCHOR_FOR.get(area)
        if key and key not in first_anchor:
            first_anchor[key] = p['id']
# Keep old type-group links working at the first matching record in the combined list.
for kind, (_, _, anchor) in PUBLICATION_TYPES.items():
    first = next((p for p in ordered if p['type'] == kind), None)
    if first: first_anchor[anchor] = first['id']
first_accepted = next((p for p in ordered if not is_preprint(p)), None)
if first_accepted: first_anchor['peer-reviewed'] = first_accepted['id']
for year in publication_years:
    first_anchor[f'year-{year}'] = next(p['id'] for p in ordered if p['year'] == year)

def area_anchors(p):
    return ''.join(f'<span id="{key}" class="legacy-anchor"></span>'
                   for key, pid in first_anchor.items() if pid == p['id'])

listing = ''.join(area_anchors(p) + publication(p, labels_by_id[p['id']]) for p in ordered)
sections = (f'<section class="publication-group publication-catalogue" id="publication-list" '
            f'aria-labelledby="publication-key">{publication_key}{listing}</section>')
pub_body = f'''<header class="page-heading publications-heading"><p class="eyebrow">Research output</p><h1>Publications</h1><p class="lead">A record of my research, in print and in progress, from newest to oldest.</p></header>
<div class="publications-summary"><dl class="publication-metrics">{metric_html}</dl><div class="publication-actions"><a class="btn" data-kind="scholar" href="https://scholar.google.com/citations?user=LWB_NzwAAAAJ">{icon("scholar")}<span>Google Scholar</span>{icon("external", "icon icon-trail")}</a><a class="btn" data-kind="cv" href="files/cv/tariq.pdf" target="_blank" rel="noopener">{icon("pdf")}<span>Download CV</span>{icon("external", "icon icon-trail")}</a></div></div><p class="metrics-note">{metric_note}</p>
<div class="publication-sections">{sections}<section class="section" id="resources"><h2>Code &amp; data</h2><div class="resource-list"><article><h3><a href="https://github.com/mohsinulkabir14/guise">{icon("code")}GUISE{icon("external", "icon icon-trail")}</a></h3><p>LLM safety evaluation across request framings and cultures, grounded in real-world criminal cases.</p></article><article><h3><a href="https://github.com/lzw108/FMD">{icon("code")}FMD{icon("external", "icon icon-trail")}</a></h3><p>Scenario-induced bias benchmarking for multilingual financial misinformation detection.</p></article><article><h3><a href="https://huggingface.co/datasets/aplycaebous/BdSLIG">{icon("dataset")}BdSLIG{icon("external", "icon icon-trail")}</a></h3><p>Bangla Sign Language instruction generation dataset.</p></article><article><h3><a href="https://github.com/mdtariquzzaman/SPIP">{icon("code")}SPIP{icon("external", "icon icon-trail")}</a></h3><p>Sign Parameter Informed Prompting: reference implementation.</p></article><article><h3><a href="https://github.com/mdtariquzzaman/VITD">{icon("code")}VITD{icon("external", "icon icon-trail")}</a></h3><p>Informal Bangla embeddings and violence-inciting text detection.</p></article></div></section></div>'''

personal_data = json.loads(read('personal.json'))
personal_body = read('personal.html')
for category, entries in personal_data.items():
    ranked = category in ('anime', 'movies')
    rows = []
    for index, entry in enumerate(entries, 1):
        title = escape(entry['title']); destination = escape(entry['url'], quote=True)
        if not entry['url'].startswith('https://en.wikipedia.org/wiki/'):
            raise ValueError(f'Personal entry {entry["title"]} must link to Wikipedia')
        author = f'<p class="favorite-author">{escape(entry["author"])}</p>' if entry.get('author') else ''
        rows.append(f'<li class="favorite-row"><a class="favorite-link" href="{destination}">'
                    f'<span class="favorite-order">{index:02}</span>'
                    f'<div class="favorite-copy"><h3>{title}</h3>{author}</div>'
                    f'<span class="favorite-arrow" aria-hidden="true">{icon("external", "icon icon-trail")}</span></a></li>')
    tag = 'ol' if ranked else 'ul'
    personal_body = personal_body.replace('{{'+category.upper()+'}}', f'<{tag} class="favorites-list favorites-{category}" role="list">'+''.join(rows)+f'</{tag}>')
    personal_body = personal_body.replace('{{'+category.upper()+'_COUNT}}', str(len(entries)))

# Home's Personal teaser: one topic link per category, in personal.json order.
TOPIC_LABELS = {'anime': 'Anime', 'movies': 'Movies', 'tv': 'TV shows', 'books': 'Books', 'sports': 'Sports'}
TOPIC_ICONS = {'anime': 'tv', 'movies': 'film', 'tv': 'monitor', 'books': 'book-open', 'sports': 'football'}
personal_topics = '<ul class="topic-grid" role="list">' + ''.join(
    f'<li><a href="personal.html#{c}">{icon(TOPIC_ICONS[c])}<h3>{TOPIC_LABELS[c]}</h3></a></li>' for c in personal_data) + '</ul>'
social_links = ''.join(f'<a class="btn" data-kind="{name}" href="{escape(href, quote=True)}">'
                       f'{icon(name)}<span>{label}</span>{icon("external", "icon icon-trail")}</a>'
                       for name, label, href in SOCIAL_LINKS)
pages = [('index', 'Home', 'LLM safety, cultural bias, AI creativity in storytelling, and research in low-resource NLP methods by Md. Tariquzzaman, Junior Lecturer at IUT.', read('home.html').replace('{{NEWS}}', news_html).replace('{{PERSONAL_TOPICS}}', personal_topics).replace('{{SOCIAL_LINKS}}', social_links)),
         ('publications', 'Publications', 'Publications, preprints, code, and datasets by Md. Tariquzzaman.', pub_body),
         ('cv', 'CV', 'Education, research and teaching experience, technical skills, industry experience, awards, certifications, and languages of Md. Tariquzzaman.', read('cv.html')),
         ('personal', 'Personal', 'Favorite anime, movies, TV shows, books, and sports beyond the academic work of Md. Tariquzzaman.', personal_body)]

PERSON = {'@type': 'Person', '@id': SITE + '#person', 'name': ME,
          'alternateName': ['Tariquzzaman', 'Md Tariquzzaman', 'Tariquzzaman Md'],
          'jobTitle': 'Junior Lecturer', 'url': SITE, 'image': SITE + 'profile.jpg',
          'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Islamic University of Technology', 'url': 'https://www.iutoic-dhaka.edu/'},
          'memberOf': {'@type': 'ResearchOrganization', 'name': 'Systems and Software Lab', 'url': 'https://cse.iutoic-dhaka.edu/ssl'},
          'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'Islamic University of Technology'},
          'knowsAbout': ['LLM safety', 'Cultural bias', 'AI creativity & storytelling', 'Low resource methods for NLP'],
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
            'datePublished': p.get('date') or p['year'], 'inLanguage': 'en', 'url': url,
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
    nav = ''.join(f'<a href="{asset_prefix}{s}.html"' + (' aria-current="page"' if s == current else '') + f'>{icon("cursor", "icon nav-cursor")}<span>{t}</span></a>' for s, t, _, _ in pages)
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow">'
    asset = asset_prefix
    body = expand_icons(body)
    # Restore a saved day/night choice before styles load, without hiding native controls.
    theme_init = ('<script>try{const theme=localStorage.getItem("tariq-theme");'
                  'if(theme==="light"||theme==="dark")document.documentElement.dataset.theme=theme;'
                  '}catch(_){}</script>')
    footer_links = [('mail', 'Email', 'mailto:tariquzzaman@iut-dhaka.edu')] + list(SOCIAL_LINKS) + [
        ('arrow-up', 'Back to top', '#main')]
    footer = ''.join(f'<a href="{escape(href, quote=True)}">{icon(name, "icon footer-icon")}<span>{label}</span></a>'
                     for name, label, href in footer_links)
    theme_mobile = '<button class="theme-toggle theme-toggle-mobile" type="button" aria-label="Switch to dark theme" title="Switch to dark theme"><span aria-hidden="true">Day / night</span></button>'
    theme_desktop = '<button class="theme-toggle theme-toggle-desktop" type="button" aria-label="Switch to dark theme" title="Switch to dark theme"><span aria-hidden="true">Day / night</span></button>'
    # Holds or plays the decorative pixel animations (assets/scenes.js); shown with JavaScript.
    motion_icons = icon('pause', 'icon icon-pause') + icon('play', 'icon icon-play')
    motion_mobile = f'<button class="motion-toggle motion-toggle-mobile" type="button" aria-pressed="false" aria-label="Pause animations" title="Pause animations">{motion_icons}</button>'
    motion_desktop = f'<button class="motion-toggle motion-toggle-desktop" type="button" aria-pressed="false" aria-label="Pause animations" title="Pause animations">{motion_icons}</button>'
    # Publications' back-to-top arrow stays fixed at the bottom right; app.js pops it up once the page scrolls down.
    back_to_top = f'<a class="btn back-to-top" href="#main" aria-label="Back to top" title="Back to top">{icon("arrow-up")}</a>' if slug == 'publications' else ''
    header_controls = f'<div class="header-controls">{motion_mobile}{theme_mobile}</div>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{theme_init}<title>{escape(page_title)}</title><meta name="description" content="{escape(description, quote=True)}">{robots}<meta name="google-site-verification" content="{GSC_TOKEN}"><meta name="msvalidate.01" content="{BING_TOKEN}"><meta name="theme-color" content="#f2e9d8" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#181d30" media="(prefers-color-scheme: dark)"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(page_title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}profile.jpg"><meta property="og:image:alt" content="Md. Tariquzzaman"><meta name="twitter:card" content="summary"><meta name="twitter:site" content="@mdtariquzzaman_"><meta name="twitter:creator" content="@mdtariquzzaman_"><meta name="twitter:title" content="{escape(page_title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SITE}profile.jpg"><link rel="icon" href="{asset}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{asset}assets/style.css?v={ASSET_VERSION}"><link rel="stylesheet" href="{asset}assets/interactions.css?v={ASSET_VERSION}">{head_extra}</head><body class="page-{slug}"><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-title-strip"><span class="header-title">Md. Tariquzzaman</span>{header_controls}</div><div class="header-inner"><nav aria-label="Main navigation">{nav}</nav><div class="header-tools">{motion_desktop}{theme_desktop}</div></div></header><div class="site-shell"><main id="main">{body}</main><footer class="site-footer"><p>© 2026 Md. Tariquzzaman</p><div>{footer}</div></footer>{back_to_top}</div><script src="{asset}assets/app.js?v={ASSET_VERSION}"></script><script src="{asset}assets/scenes.js?v={ASSET_VERSION}"></script></body></html>'''

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
llms = '# Md. Tariquzzaman\n\nAcademic website: '+SITE+'\n\nResearch: LLM safety; cultural bias; AI creativity in storytelling; Low resource methods for NLP. I am particularly interested in applying language models to real-world problems.\n\n## Profiles\n- [Bluesky](https://bsky.app/profile/mdtariquzzaman.bsky.social)\n- [X](https://x.com/mdtariquzzaman_)\n\n## Pages\n- [Publications]('+SITE+'publications.html)\n- [CV]('+SITE+'cv.html)\n\n## Publications\n' + ''.join(f'- [{p["title"]}]({SITE}publications.html#{p["id"]})\n' for p in papers)
(ROOT / 'llms.txt').write_text(llms)
print(f'Built {len(pages)} static pages, {len(papers)} paper redirects, plus 404.html, sitemap.xml, robots.txt, and llms.txt.')
