# fb-post-images

Images for automated Facebook Page posts (ORNATEit, Technoloxia Bangladesh, vQ Export Import, CFDE Edmonton, CiCiO OÜ).

- `logos/` – one logo per Page (`ornateit.png`, `technoloxia.png`, `vq.png`, `cfde.png`, `cicio.png`)
- `fonts/` – Hind Siliguri (Bengali + Latin) and Poppins; include with `fonts/fonts.css`
- `tools/render.py` – renders an HTML file to a 1080x1080 PNG: `python3 tools/render.py in.html out.png`
- `tools/make_post.py` – builds a branded 1080x1080 post image from a small JSON spec (see the docstring at the top of the file)
- `tools/examples/` – example post designs
- `posts/<page>/<date>.png` – published post images

Public image link format:
`https://raw.githubusercontent.com/technoloxiabd/fb-post-images/main/posts/<page>/<date>.png`
