import os
import sys
sys.path.append('Stiman-Dessert-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','stimandessert.settings')
import django
django.setup()
from tienda.models import Producto

MEDIA_PROD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'productos')
files = os.listdir(MEDIA_PROD_DIR) if os.path.isdir(MEDIA_PROD_DIR) else []
files_lower = [f.lower() for f in files]

updated = []
for p in Producto.objects.all():
    if p.image and p.image.name:
        continue
    name = p.name.lower()
    # try exact match by slug-like name
    candidates = []
    for f in files:
        fn = f.lower()
        # match if product name tokens appear in filename
        tokens = [t for t in name.replace('-', ' ').replace('_',' ').split() if t]
        if all(any(t in part for part in [fn]) for t in tokens[:2]):
            candidates.append(f)
    # fallback: any filename contains first token
    if not candidates and name.split():
        token = name.split()[0]
        for f in files:
            if token in f.lower():
                candidates.append(f)
    # also try filenames that start with token
    if not candidates:
        for f in files:
            if f.lower().startswith(name.replace(' ', '_')) or f.lower().startswith(name.replace(' ', '')):
                candidates.append(f)
    if candidates:
        chosen = candidates[0]
        rel_path = os.path.join('productos', chosen).replace('\\','/')
        Producto.objects.filter(pk=p.pk).update(image=rel_path)
        updated.append((p.pk, p.name, rel_path))

print('Updated:', len(updated))
for u in updated:
    print(u)

print('\nRemaining without image:')
for p in Producto.objects.filter(image='')[:50]:
    print(p.pk, p.name)
