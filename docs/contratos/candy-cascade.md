# Contrato — Candy Cascade (card Sweet Bonanza)

Slot demo **6×5**, pay anywhere, cascatas, free spins e multiplicadores. Play money — **sem dinheiro real**.

**Base URL:** `{API}/api/v1/slots/candy-cascade/`

**Card na home:** `GET /api/v1/games/sweet-bonanza/` (`play_kind=slot`, `play_mesa_slug=candy-cascade`).

**Frontend:** rota `#/sweet-bonanza?game=sweet-bonanza` (`play.client_route` + `play.card_slug`).

**Chances:** [chances-demo.md](./chances-demo.md)

**Aviso fixo:** `jogo.aviso_demo` e `aviso_demo` na resposta do giro: `"Jogo de demonstração. Sem dinheiro real."`

---

## Configuração

### `GET /api/v1/slots/candy-cascade/?jogo=candy-cascade`

**200 OK** (trecho)

```json
{
  "jogo": {
    "slug": "candy-cascade",
    "card_slug": "sweet-bonanza",
    "nome": "Candy Cascade",
    "titulo_card": "Sweet Bonanza",
    "nome_exibicao_modal": "Sweet Bonanza",
    "client_route": "#/sweet-bonanza",
    "rtp": "96.0%",
    "saldo_inicial": "1000.00",
    "grade": { "colunas": 6, "linhas": 5 },
    "cluster_minimo": 8,
    "aviso_demo": "Jogo de demonstração. Sem dinheiro real.",
    "chances": { "percentual_casa": "55.00", "percentual_usuario": "45.00" },
    "opcoes": {
      "apostas_permitidas": ["0.20", "0.50", "1.00", "2.00", "5.00", "10.00", "20.00"],
      "aposta_extra_markup": "0.25",
      "comprar_free_spins_mult": "100",
      "max_ganho_por_giro": "5000"
    },
    "bonus": {
      "scatters_para_ativar": 4,
      "free_spins_iniciais": 10,
      "retrigger_giros": 5
    }
  },
  "simbolos": [],
  "regras_resumo": [],
  "historico_recente": []
}
```

### `GET /api/v1/games/sweet-bonanza/`

Retorna `card`, `play` (com `client_route`: `#/sweet-bonanza`, APIs em `play.api`) e `slot` = payload de config acima.

---

## Sessão

### `POST /api/v1/slots/candy-cascade/sessoes/`

```json
{ "jogo_slug": "candy-cascade", "apelido": "Demo" }
```

**201** — `sessao_id`, `saldo`, `estado` (`mode`, `free_spins_left`, `free_spins_total`, `aposta_ref`, `extra_bet`).

### `GET /api/v1/slots/candy-cascade/sessoes/{sessao_id}/`

---

## Girar

### `POST /api/v1/slots/candy-cascade/girar/`

```json
{
  "sessao_id": "uuid",
  "aposta": "1.00",
  "aposta_extra": false,
  "comprar_free_spins": false
}
```

| Campo | Descrição |
|-------|-----------|
| `aposta` | Um dos valores em `opcoes.apostas_permitidas` |
| `aposta_extra` | +25% no custo do giro base; dobra peso do scatter |
| `comprar_free_spins` | Custa `100×` aposta; inicia rodada em modo free spin |

**201 Created** (trecho)

```json
{
  "giro_id": 1,
  "modo": "base",
  "aposta_cobrada": "1.00",
  "premio": "12.50",
  "saldo": "1011.50",
  "cascatas": [
    {
      "ganhos": [{ "simbolo": "cherry", "contagem": 8, "premio": "3.00", "celulas": [[0, 1], []] }],
      "premio_parcial": "3.00",
      "grade": [[null]],
      "multiplicadores": [[null]]
    }
  ],
  "grade": [[]],
  "multiplicadores": [[]],
  "estado": {},
  "aviso_demo": "Jogo de demonstração. Sem dinheiro real."
}
```

Eventos em `cascatas`: `pagamento_scatter`, `multiplicadores_aplicados`, `teto_maximo`.

---

## Erros

**400** — `{ "erro": { "codigo": "...", "mensagem": "..." } }`

| código | quando |
|--------|--------|
| `jogo_indisponivel` | sem jogo ativo |
| `sessao_invalida` | UUID inexistente |
| `aposta_invalida` | valor fora da lista |
| `saldo_insuficiente` | compra de bônus ou giro pago |
| `aposta_fora_limite` | fora do min/max do jogo |

---

## Admin

| Modelo | Uso |
|--------|-----|
| `CandyCascadeJogo` | Nome, slug, limites, chances |
| `CandyCascadeSessao` | Saldo demo + `estado` JSON |
| `CandyCascadeGiro` | Histórico de giros |

Seed: `python manage.py seed_candy_cascade`