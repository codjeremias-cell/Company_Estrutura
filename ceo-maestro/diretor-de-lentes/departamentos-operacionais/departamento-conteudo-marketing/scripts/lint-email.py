#!/usr/bin/env python3
"""
lint-email.py — Auditor automático de e-mail HTML bulletproof.

Verifica mecanicamente as RO-EM (Regras de Ouro — Email Marketing HTML) contra
um arquivo .html gerado pela skill `email-marketing-html`. Não é estético:
cada checagem aqui existe porque um cliente de e-mail real (Outlook, Gmail,
Apple Mail, Yahoo) quebra sem ela.

Uso:
    python3 lint-email.py caminho/para/email.html

Saída: PASS/FAIL por regra + resumo. Exit code 0 = tudo passou (nenhum FAIL).
Exit code 1 = pelo menos um FAIL. WARN nunca muda o exit code (é aviso de
conteúdo, não de estrutura).
"""
import re
import sys
from pathlib import Path


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    return text


def check_doctype(html):
    ok = html.strip().lower().startswith("<!doctype html>")
    return ok, "DOCTYPE html presente no topo do arquivo" if ok else \
        "Falta <!DOCTYPE html> na primeira linha (necessário para modo standards em todos os clientes)"


def check_viewport(html):
    ok = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I))
    return ok, "meta viewport presente" if ok else \
        "Falta <meta name=\"viewport\" ...> — sem isso o zoom mobile fica fora do controle da skill"


def check_no_div_layout(html):
    # Exceção única e deliberada: a <div> de pré-cabeçalho oculto (texto de preview
    # ao lado do assunto na caixa de entrada) nunca renderiza — display:none real,
    # não layout. Qualquer OUTRA div é falha (RO-EM1).
    all_divs = re.findall(r"<div\b[^>]*>", html, re.I)
    offending = [
        d for d in all_divs
        if not (re.search(r"display\s*:\s*none", d, re.I) and
                (re.search(r"mso-hide\s*:\s*all", d, re.I) or re.search(r"overflow\s*:\s*hidden", d, re.I)))
    ]
    ok = len(offending) == 0
    return ok, "Nenhuma <div> de layout (só a div oculta de pré-cabeçalho, se houver, é permitida)" if ok else \
        f"{len(offending)} <div> de LAYOUT encontrada(s) — layout de e-mail é só table/tr/td (RO-EM1); div quebra em Outlook/Windows Mail. (A única exceção é a div display:none do pré-cabeçalho.)"


def check_no_modern_layout_css(html):
    # Correção 2026-07-20 (auditoria, lente dev-senior): a versão anterior comparava
    # substring literal ("display:flex", "display: flex") e não pegava variações de
    # espaço como "display :flex" ou "display  :  flex" nem quebra de linha entre a
    # propriedade e o valor. Regex tolera qualquer quantidade de espaço/tab/newline
    # em volta dos dois-pontos.
    banned_props = {
        "display": ["flex", "grid"],
        "position": ["absolute", "fixed"],
    }
    found = []
    lowered = html.lower()
    for prop, values in banned_props.items():
        for value in values:
            pattern = re.compile(re.escape(prop) + r"\s*:\s*" + re.escape(value), re.I)
            if pattern.search(lowered):
                found.append(f"{prop}:{value}")
    ok = len(found) == 0
    return ok, "Nenhum CSS de layout moderno (flex/grid/position) encontrado" if ok else \
        f"CSS não suportado por Outlook encontrado: {', '.join(found)} (RO-EM1)"


def check_tables_bulletproof(html):
    tables = re.findall(r"<table\b[^>]*>", html, re.I)
    bad = []
    for i, t in enumerate(tables, 1):
        missing = []
        if not re.search(r'role\s*=\s*["\']presentation["\']', t, re.I):
            missing.append("role=\"presentation\"")
        if not re.search(r'cellspacing\s*=\s*["\']0["\']', t, re.I):
            missing.append('cellspacing="0"')
        if not re.search(r'cellpadding\s*=\s*["\']0["\']', t, re.I):
            missing.append('cellpadding="0"')
        if not re.search(r'border\s*=\s*["\']0["\']', t, re.I):
            missing.append('border="0"')
        if missing:
            bad.append(f"  tabela #{i}: falta {', '.join(missing)}")
    ok = len(bad) == 0
    detail = "Todas as tabelas têm role=presentation + cellspacing/cellpadding/border=0" if ok else \
        "Tabela(s) sem os atributos bulletproof completos (RO-EM1):\n" + "\n".join(bad)
    return ok, detail


def check_images(html):
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    if not imgs:
        return True, "Nenhuma <img> no arquivo (nada a checar)"
    bad = []
    for i, tag in enumerate(imgs, 1):
        missing = []
        if not re.search(r'\balt\s*=\s*["\']', tag, re.I):
            missing.append("alt=\"...\" (obrigatório — RO-EM5)")
        style_match = re.search(r'style\s*=\s*"([^"]*)"', tag, re.I)
        style = style_match.group(1).lower() if style_match else ""
        if "display:block" not in style.replace(" ", ""):
            missing.append("display:block no style inline")
        if "border:0" not in style.replace(" ", "") and 'border="0"' not in tag.lower():
            missing.append("border:0 (evita moldura azul em alguns clientes)")
        if "max-width" not in style:
            missing.append("max-width no style inline (senão a imagem estoura em telas largas)")
        if missing:
            bad.append(f"  img #{i}: falta {', '.join(missing)}")
    ok = len(bad) == 0
    detail = f"{len(imgs)} imagem(ns), todas com alt + display:block + border:0 + max-width" if ok else \
        "Imagem(ns) sem os atributos bulletproof (RO-EM5):\n" + "\n".join(bad)
    return ok, detail


def check_cta_not_image(html):
    # Heurística: <a href=...><img ...></a> sem nenhum texto VISÍVEL entre as tags =
    # provável botão-imagem. Correção 2026-07-20 (auditoria, lente especialista-seguranca
    # + dev-senior): a versão anterior exigia "nada além do <img>" com \s* — um texto
    # escondido (display:none) entre o <img> e o </a> bastava para escapar da checagem,
    # mesmo que continuasse invisível para o usuário real com imagem bloqueada. Agora
    # removemos elementos display:none antes de avaliar se sobrou texto visível.
    anchors = re.findall(r"<a\b[^>]*>(.*?)</a>", html, re.I | re.S)
    bad = 0
    for inner in anchors:
        if not re.search(r"<img\b", inner, re.I):
            continue
        visible = re.sub(
            r"<(span|div|p|td|a)\b[^>]*display\s*:\s*none[^>]*>.*?</\1>", "", inner,
            flags=re.I | re.S,
        )
        visible = re.sub(r"<img\b[^>]*>", "", visible, flags=re.I)
        visible_text = re.sub(r"<[^>]+>", "", visible).strip()
        if not visible_text:
            bad += 1
    ok = bad == 0
    return ok, "Nenhum link que é só uma <img> sem texto visível (CTA não é imagem — RO-EM3)" if ok else \
        f"{bad} link(s) que envolvem uma <img> sem NENHUM texto visível ao lado (texto oculto com display:none não conta) — se for o CTA principal, vira invisível quando o cliente bloqueia imagem (RO-EM3). OK se for só o banner clicável, não o botão."


def check_max_width_600(html):
    ok = "max-width: 600px" in html.replace('"', '') or "max-width:600px" in html.replace(" ", "")
    return ok, "max-width:600px encontrado (largura padrão de e-mail)" if ok else \
        "Não encontrei max-width:600px — confirme que o wrapper principal está limitado (RO-EM1 recomenda 600px)"


def check_mso_conditional(html):
    ok = "[if mso]" in html or "[if gte mso" in html
    return ok, "Comentário condicional MSO (Outlook) presente" if ok else \
        "Sem <!--[if mso]> — confirme se o layout precisa de ghost table para o Outlook desktop (RO-EM4); templates de 1 coluna simples podem dispensar"


def check_unsubscribe(html):
    text = html.lower()
    keywords = ["descadastr", "cancelar inscri", "unsubscribe", "não quero mais receber", "nao quero mais receber"]
    ok = any(k in text for k in keywords)
    # Correção 2026-07-20 (auditoria, lente auditor-responsabilidades): era WARN,
    # promovido a FAIL — descadastro é obrigatório por LGPD/boas práticas de ESP, não
    # é uma preferência estética que se possa ignorar num "0 FAIL aprovado".
    return ok, "Link/menção de descadastro encontrado no rodapé" if ok else \
        "Não encontrei texto de descadastro (\"descadastrar\", \"cancelar inscrição\"...) — obrigatório por LGPD/boas práticas de ESP (RO-EM6). Não entregar como final sem isso; em rascunho de layout, deixe pelo menos o placeholder [LINK_DE_DESCADASTRO] explícito."


def check_no_leftover_placeholders(html):
    # RO-EM: nenhum e-mail marcado como pronto para envio pode conter um placeholder
    # de conteúdo esquecido (ex.: "[TÍTULO_PRINCIPAL]" indo pro cliente real). Isto é
    # esperado em template/template-base.html (é o scaffold, antes do preenchimento) —
    # rodar o linter ali mostrando este FAIL é correto: o scaffold cru nunca deve ser
    # entregue como e-mail final.
    matches = re.findall(r"\[[A-ZÀ-Ú0-9][A-ZÀ-Ú0-9_ \-/]{2,60}\]", html)
    ok = len(matches) == 0
    sample = ", ".join(sorted(set(matches))[:6])
    return ok, "Nenhum placeholder de conteúdo (ex.: [TÍTULO_PRINCIPAL]) sobrando no HTML" if ok else \
        f"{len(matches)} placeholder(s) de conteúdo ainda não preenchido(s): {sample}{'...' if len(set(matches)) > 6 else ''} — preencher com o conteúdo real do briefing antes de entregar como e-mail final (RO-01, nunca enviar rascunho como pronto)."


def check_generic_alt(html):
    # Heurística de conteúdo (por isso WARN, não FAIL — pode haver falso positivo):
    # alt text genérico não descreve a imagem para quem usa leitor de tela ou está
    # com imagem bloqueada, o que na prática anula o propósito do atributo (RO-EM5).
    generic = {
        "imagem", "image", "img", "banner", "foto", "picture", "logo", "figura",
        "photo", "graphic", "grafico", "gráfico", "sem descricao", "sem descrição",
        "placeholder", "untitled", "sem título", "sem titulo",
    }
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    bad = []
    for i, tag in enumerate(imgs, 1):
        m = re.search(r'\balt\s*=\s*"([^"]*)"', tag, re.I)
        if not m:
            continue  # já reportado por check_images (FAIL)
        alt = m.group(1).strip().lower()
        if alt == "" or alt in generic or re.fullmatch(r"(imagem|image|img|foto)\s*\d*", alt):
            bad.append(f"  img #{i}: alt=\"{m.group(1)}\"")
    ok = len(bad) == 0
    return ok, "Nenhum alt genérico/vazio encontrado (todos descrevem a imagem)" if ok else \
        "alt text genérico ou vazio em imagem de conteúdo (RO-EM5) — descreva o que a imagem TRANSMITE (ex.: \"40% de desconto em toda a loja\"), não um rótulo genérico. alt=\"\" só é aceitável em imagem puramente decorativa:\n" + "\n".join(bad)


def check_dangerous_uri(html):
    # Checagem de segurança (lente especialista-seguranca): javascript: URIs e
    # handlers inline (onclick etc.) não funcionam na maioria dos clientes de e-mail
    # e a presença deles costuma indicar copy-paste de template web ou injeção —
    # nenhum dos dois pertence a um e-mail bulletproof.
    findings = []
    if re.search(r'href\s*=\s*["\']?\s*javascript:', html, re.I):
        findings.append("href=\"javascript:...\"")
    if re.search(r'src\s*=\s*["\']?\s*javascript:', html, re.I):
        findings.append("src=\"javascript:...\"")
    if re.search(r"<script\b", html, re.I):
        findings.append("<script> (clientes de e-mail removem ou o Gmail pode bloquear a mensagem inteira)")
    if re.search(r'\son(click|load|error|mouseover|focus)\s*=\s*["\']', html, re.I):
        findings.append("atributo on*= (onclick/onload/onerror/...) inline")
    ok = len(findings) == 0
    return ok, "Nenhuma javascript: URI, <script> ou handler inline encontrado" if ok else \
        "Conteúdo não permitido/perigoso em e-mail encontrado (RO-EM1/segurança): " + "; ".join(findings)


def check_relative_image_paths(html):
    # WARN, não FAIL (correção 2026-07-20, lente inovacao-melhorias: uma checagem FAIL
    # aqui invalidaria retroativamente o exemplo-02, que usa caminho relativo de
    # propósito para preview local — documentado em exemplo-02-briefing.md). Em
    # produção, e-mail não tem "diretório atual": todo <img src> precisa ser URL
    # absoluta (https://...) hospedada, senão quebra em 100% dos clientes reais.
    imgs = re.findall(r'<img\b[^>]*\bsrc\s*=\s*"([^"]*)"', html, re.I)
    relative = [
        src for src in imgs
        if src and not re.match(r"^(https?:)?//|^https?://|^\[", src, re.I) and not src.startswith("data:")
    ]
    ok = len(relative) == 0
    sample = ", ".join(relative[:5])
    return ok, "Todas as imagens usam URL absoluta ou placeholder" if ok else \
        f"{len(relative)} <img src> com caminho relativo ({sample}) — ok para preview local (ex.: exemplo few-shot), mas e-mail de produção exige URL absoluta hospedada (https://...), senão a imagem quebra em todo cliente real."


RULES = [
    ("DOCTYPE", check_doctype, "FAIL"),
    ("Viewport", check_viewport, "FAIL"),
    ("Sem <div> de layout", check_no_div_layout, "FAIL"),
    ("Sem CSS moderno (flex/grid/position)", check_no_modern_layout_css, "FAIL"),
    ("Tabelas bulletproof", check_tables_bulletproof, "FAIL"),
    ("Imagens bulletproof", check_images, "FAIL"),
    ("Sem placeholder de conteúdo sobrando", check_no_leftover_placeholders, "FAIL"),
    ("Sem URI perigosa / script inline", check_dangerous_uri, "FAIL"),
    ("Link de descadastro", check_unsubscribe, "FAIL"),
    ("CTA não é imagem pura", check_cta_not_image, "WARN"),
    ("alt text não genérico", check_generic_alt, "WARN"),
    ("Wrapper max-width:600px", check_max_width_600, "WARN"),
    ("Ghost table MSO (Outlook)", check_mso_conditional, "WARN"),
    ("Imagens com URL absoluta", check_relative_image_paths, "WARN"),
]


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 lint-email.py caminho/para/email.html")
        sys.exit(2)
    path = sys.argv[1]
    html = load(path)

    fails = 0
    print(f"\nlint-email.py — auditando {path}\n" + "=" * 60)
    for name, fn, severity in RULES:
        ok, detail = fn(html)
        if ok:
            tag = "PASS"
        else:
            tag = "FAIL" if severity == "FAIL" else "WARN"
            if severity == "FAIL":
                fails += 1
        print(f"[{tag:4}] {name}")
        for line in detail.split("\n"):
            print(f"        {line}")
    print("=" * 60)
    if fails:
        print(f"RESULTADO: {fails} FAIL — corrigir antes de entregar.\n")
        sys.exit(1)
    else:
        print("RESULTADO: 0 FAIL — estrutura bulletproof aprovada (WARN acima é revisão de conteúdo, não bloqueia).\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
