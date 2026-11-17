# Contrato — Wolf Gold (PlayHub)

Slot **5×3**, 25 linhas, free spins e money respin, play money.

**Base URL:** `{API}/api/v1/slots/wolf-gold/`

**Chances demo:** [chances-demo.md](./chances-demo.md) (`jogo.chances`).

---

## Configuração

### `GET /api/v1/slots/wolf-gold/`

Query opcional: `?jogo=wolf-gold`.

**200 OK** (trecho)

```json
{
  "jogo": {
    "slug": "wolf-gold",
    "nome": "Wolf Gold",
    "rtp": "96.0%",
    "saldo_inicial": "10000.00",
    "aposta_minima": "0.25",
    "aposta_maxima": "125.00",
    "linhas": 25,
    "jackpots": { "mini": "20x", "major": "50x", "mega": "1000x" },
    "chances": {
      "percentual_casa": "55.00",
      "percentual_usuario": "45.00"
    }
  },
  "simbolos": [],
  "paylines": [],
  "historico_recente": []
}
```

### Card na grade

`GET /api/v1/games/wolf-gold/` → `card` + `play.kind === "slot"` + `slot`.

| Campo no catálogo | Valor seed |
|-------------------|------------|
| `play_kind` | `slot` |
| `play_mesa_slug` | `wolf-gold` |

---

## Sessão e girar

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `sessoes/` | Cria sessão com estado inicial |
| GET | `sessoes/{sessao_id}/` | Saldo e `estado` (free spins / respin) |
| POST | `girar/` | Body `{ "sessao_id", "aposta" }` — viés de chances só no giro **base pago** |

Modo `forcar` (grade fixa): apenas com `DEBUG=true` no servidor.