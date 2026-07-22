# AI Product Description Generator for Odoo

Generate high-converting product descriptions in **one click** — in any tone and any
language — using the AI provider of your choice, **including free ones**.

> Odoo module · works with OpenAI, **Groq (free)**, **Google Gemini (free)**,
> **OpenRouter (free)**, Anthropic (Claude), and **Ollama (local, free)**.

![banner](ai_product_description/static/description/banner.png)

---

## ✨ Features

- 🪄 **One-click generation** — an *AI Description* button on every product.
- 🎯 **Tone control** — professional, friendly, persuasive, luxury, technical, playful.
- 📏 **Length control** — short, medium, or long.
- 🌍 **Any language** — generate descriptions in the language you sell in.
- 🏷️ **Your keywords** — emphasize the selling points that matter.
- 👀 **Review before applying** — nothing is overwritten until you confirm.
- 🛒 Apply to the **Sales Description** or the **eCommerce (website) description**.
- 🔌 **Multi-provider** — pick paid quality or a **100% free** setup.

## 💸 Use it for free

You do **not** need a paid AI subscription. Any of these work out of the box:

| Provider | Cost | Get a key |
|---|---|---|
| **Groq** | Free API key, very fast | <https://console.groq.com/keys> |
| **Google Gemini** | Generous free tier | <https://aistudio.google.com/apikey> |
| **OpenRouter** | Free models available | <https://openrouter.ai/keys> |
| **Ollama** | 100% local, no key | <https://ollama.com> |
| OpenAI / Anthropic | Paid (premium quality) | provider dashboard |

## 🚀 Installation

1. Copy the `ai_product_description` folder into your Odoo `addons` path.
2. Update the apps list and install **AI Product Description Generator**.
3. Go to **Settings → AI Product Description**, pick a provider, and paste your API key.
4. Open any product and click **AI Description**.

## ⚙️ Configuration

**Settings → AI Product Description:**

- **Provider** — choose your AI provider.
- **API Key** — paste your key (not needed for Ollama).
- **Model** — leave empty for a sensible default per provider.
- **API Base URL** — advanced; override only for custom endpoints/proxies.
- **Creativity** — 0 (precise) → 1 (creative).

## 🔒 Privacy

Your product data is sent only to the AI provider **you** select. Nothing is routed
through any other third-party service.

## 🧩 Supported Odoo versions

| Version | Branch |
|---|---|
| Odoo 19 | [`19.0`](../../tree/19.0) |
| Odoo 18 | [`18.0`](../../tree/18.0) |
| Odoo 17 | [`17.0`](../../tree/17.0) |

## 📄 License

[LGPL-3](LICENSE)

## 👤 Author

**Tughral Khattak** — Software Engineer · Odoo Developer
