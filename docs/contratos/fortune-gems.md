# Contrato — Fortune Gems (PlayHub)

Slot **3×1** (três carretéis), play money. Sem dinheiro real.

**Base URL:** `{API}/api/v1/slots/fortune-gems/`

**Chances demo:** [chances-demo.md](./chances-demo.md) (`jogo.chances`).

---

## Configuração

### `GET /api/v1/slots/fortune-gems/`

Query opcional: `?jogo=fortune-gems` (slug).

**200 OK** (trecho)

```json
{
  "jogo": {
    "slug": "fortune-gems",
    "nome": "Fortune Gems",
    "rtp": "96.5%",
    "saldo_inicial": "25450.00",
    "aposta_minima": "10.00",
    "aposta_maxima": "1000.00",
    "jackpot_exibicao": "1489200.50",
    "chances": {
      "percentual_casa": "55.00",
      "percentual_usuario": "45.00"
    }
  },
  "simbolos": [],
  "linhas_ativas": 5,
  "historico_recente": []
}
```

### Card na grade

`GET /api/v1/games/fortune-gems/` → `card` (tipo `Game` com `percentual_casa` / `percentual_usuario`) + `play.kind === "slot"` + `slot` (payload acima).

| Campo no catálogo | Valor seed |
|-------------------|------------|
| `play_kind` | `slot` |
| `play_mesa_slug` | `fortune-gems` |

---

## Sessão e girar

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `sessoes/` | Cria sessão demo |
| GET | `sessoes/{sessao_id}/` | Saldo e último giro |
| POST | `girar/` | Body `{ "sessao_id", "aposta" }` — **inalterado** pelas chances |

Erros: `{ "erro": { "codigo", "mensagem" } }` → **400**.