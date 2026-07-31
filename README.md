# Instagram followers pro Widgy

Automatická varianta pro profesionální Instagram účet. Skript načte počet sledujících přes oficiální Instagram API a uloží jednoduchý `instagram.json`, který může číst Widgy.

## Co z toho vznikne

Veřejný JSON endpoint:

```text
https://TVUJ_GITHUB.github.io/instagram-widgy-auto/instagram.json
```

Příklad obsahu:

```json
{
  "username": "oliverblaha.cz",
  "followers": 1234,
  "followers_display": "1 234",
  "following": 321,
  "posts": 87,
  "updated_at": "2026-07-31T20:00:00Z"
}
```

## Nejjednodušší postup

1. Vytvoř na GitHubu nový repozitář třeba `instagram-widgy-auto`.
2. Nahraj do něj všechny soubory z této šablony.
3. V GitHubu otevři **Settings > Secrets and variables > Actions**.
4. Přidej secret:
   - název: `IG_ACCESS_TOKEN`
   - hodnota: tvůj dlouhodobý Instagram User Access Token
5. Pokud používáš starší Facebook/Page napojení místo Instagram Login, přidej i repository variable nebo secret:
   - název: `IG_USER_ID`
   - hodnota: tvoje Instagram User ID
   - volitelně variable `IG_API_HOST` nastav na `https://graph.facebook.com`
6. V GitHubu otevři **Settings > Pages**.
7. Nastav **Deploy from a branch**.
8. Vyber větev `main` a složku `/root`.
9. V záložce **Actions** spusť workflow **Update Instagram stats** ručně.
10. Otevři adresu:

```text
https://TVUJ_GITHUB.github.io/instagram-widgy-auto/instagram.json
```

## Widgy

1. Otevři **Widgy**.
2. Vytvoř nový **Home Widget**.
3. Přidej text pro počet sledujících.
4. Jako data použij JSON endpoint z GitHub Pages.
5. Vyber hodnotu:

```text
followers_display
```

Můžeš přidat i:

```text
username
posts
following
updated_at
```

## Důležité

Nikdy nevkládej Instagram access token přímo do Widgy. Widget by ho mohl zbytečně vystavit. Token patří jen do GitHub Secretu `IG_ACCESS_TOKEN`.

Token může být potřeba pravidelně obnovovat. Meta má pro Instagram dlouhodobé tokeny a refresh endpoint, ale pokud token vyprší, musí se vytvořit nový.
