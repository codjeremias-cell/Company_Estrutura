#!/usr/bin/env python3
"""Gera os banners reais (PNG) do exemplo-02 (estilo banner/propaganda).

Não é parte da skill em si (a skill não gera imagem — recebe URL de imagem
pronta do usuário/design). Este script existe só para produzir os assets do
exemplo few-shot com imagens de verdade em vez de placeholder quebrado.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/truetype/google-fonts/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diagonal_gradient(w, h, c1, c2):
    img = Image.new("RGB", (w, h), c1)
    px = img.load()
    max_d = w + h
    for y in range(h):
        for x in range(0, w, 2):  # passo 2 = mais rápido, suave o bastante
            t = (x + y) / max_d
            color = lerp(c1, c2, t)
            px[x, y] = color
            if x + 1 < w:
                px[x + 1, y] = color
    return img


def center_text(draw, xy, text, fnt, fill, anchor="mm"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


# ---------------------------------------------------------------- HERO -----
# v2 — redesenhado após reprovação da lente designer-ux-ui (auditoria 2026-07-20):
# (1) fundo SÓLIDO (#9A3412, terracota), não gradiente roxo->rosa genérico de
#     "e-commerce/oferta" (teste anti-AI-slop reprovou a paleta anterior por
#     falta de justificativa própria de marca);
# (2) composição em 2 níveis (selo + 1 frase-título com o desconto embutido +
#     1 linha de apoio), não mais 3 níveis empilhados (selo + NÚMERO GIGANTE
#     isolado + stats) — o padrão "hero-metric" é proibição nominal da lente;
# (3) contraste branco/#9A3412 medido em 7.31:1 (WCAG exige 4.5:1) — ver nota
#     de cálculo em `exemplo-02-briefing.md`.
def make_hero():
    W, H = 1200, 600  # @2x para nitidez; HTML referencia em 600x300
    BRAND = (154, 52, 18)  # #9A3412 — terracota, cor única da marca fictícia
    img = Image.new("RGB", (W, H), BRAND)
    draw = ImageDraw.Draw(img)

    # selo pequeno (1 nível, não empilhado com um número gigante separado)
    tag_font = font(FONT_DIR + "Poppins-Bold.ttf", 28)
    tag_text = "OFERTA DA SEMANA"
    tag_w = draw.textlength(tag_text, font=tag_font)
    pad = 22
    rounded_rect(draw, (60, 60, 60 + tag_w + pad * 2, 60 + 54), 27, (255, 255, 255))
    draw.text((60 + pad, 60 + 27), tag_text, font=tag_font, fill=BRAND, anchor="lm")

    # título — 1 frase só, o desconto embutido no texto (não um número isolado
    # em fonte gigante própria, que é o que caracteriza o padrão banido)
    title_font = font(FONT_DIR + "Poppins-Bold.ttf", 72)
    draw.text((60, 230), "40% de desconto", font=title_font, fill=(255, 255, 255), anchor="lm")
    draw.text((60, 320), "em toda a loja", font=title_font, fill=(255, 255, 255), anchor="lm")

    # linha de apoio (prazo) — 1 único nível de apoio, sem em dash
    sub_font = font(FONT_DIR + "Poppins-Medium.ttf", 34)
    draw.text((60, 420), "Só até domingo à meia-noite. Depois volta ao normal.",
               font=sub_font, fill=(255, 224, 199), anchor="lm")

    img = img.resize((600, 300), Image.LANCZOS)
    img.save("hero-banner.png", optimize=True)
    print("hero-banner.png ok", img.size)


# ------------------------------------------------------------ URGENCY -----
def make_urgency_strip():
    W, H = 1200, 120
    img = Image.new("RGB", (W, H), (17, 24, 39))  # quase preto
    draw = ImageDraw.Draw(img)
    f = font(FONT_DIR + "Poppins-Bold.ttf", 40)
    # pêssego (#FDBA74) no lugar do amarelo — harmoniza com o terracota do
    # hero; contraste medido 10.52:1 sobre #111827 (WCAG exige 3:1 p/ texto grande)
    center_text(draw, (W / 2, H / 2), "AS PRIMEIRAS 100 COMPRAS GANHAM FRETE GRÁTIS", f, (253, 186, 116), anchor="mm")
    img = img.resize((600, 60), Image.LANCZOS)
    img.save("urgencia-strip.png", optimize=True)
    print("urgencia-strip.png ok", img.size)


# ------------------------------------------------------------ BENEFITS ----
def draw_box_icon(draw, cx, cy, s, color):
    # ícone de "caixa/pacote" simplificado (frete grátis)
    top = cy - s * 0.55
    bottom = cy + s * 0.55
    left = cx - s * 0.6
    right = cx + s * 0.6
    draw.rectangle((left, top, right, bottom), outline=color, width=10)
    draw.line((left, top + s * 0.32, right, top + s * 0.32), fill=color, width=10)
    draw.line((cx, top, cx, top + s * 0.32), fill=color, width=10)


def draw_card_icon(draw, cx, cy, s, color):
    # ícone de "cartão" simplificado (parcelamento)
    left = cx - s * 0.75
    right = cx + s * 0.75
    top = cy - s * 0.5
    bottom = cy + s * 0.5
    draw.rounded_rectangle((left, top, right, bottom), radius=18, outline=color, width=10)
    draw.rectangle((left, top + s * 0.32, right, top + s * 0.5), fill=color)


def make_benefit(filename, icon_fn, title, subtitle, bg, fg):
    W, H = 800, 460
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    icon_fn(draw, W / 2, 160, 130, fg)
    tfont = font(FONT_DIR + "Poppins-Bold.ttf", 46)
    sfont = font(FONT_DIR + "Poppins-Medium.ttf", 32)
    center_text(draw, (W / 2, 300), title, tfont, fg, anchor="mm")
    center_text(draw, (W / 2, 360), subtitle, sfont, fg, anchor="mm")
    img = img.resize((280, 161), Image.LANCZOS)
    img.save(filename, optimize=True)
    print(filename, "ok", img.size)


if __name__ == "__main__":
    make_hero()
    make_urgency_strip()
    # paleta unificada com o hero (terracota #9A3412 sobre creme quente) —
    # antes usava indigo/pink sem relação com o resto da peça
    make_benefit(
        "beneficio-frete.png", draw_box_icon,
        "Frete grátis", "acima de R$ 150",
        bg=(253, 248, 243), fg=(154, 52, 18),
    )
    make_benefit(
        "beneficio-parcela.png", draw_card_icon,
        "12x sem juros", "em qualquer cartão",
        bg=(253, 248, 243), fg=(124, 45, 18),
    )
