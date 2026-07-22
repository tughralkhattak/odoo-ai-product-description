# -*- coding: utf-8 -*-
import logging

import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Per-provider presets. `api` selects the request format:
#   * "openai"    -> OpenAI-compatible /chat/completions (OpenAI, Groq, Gemini, OpenRouter)
#   * "anthropic" -> Anthropic Messages API
#   * "ollama"    -> local Ollama /api/chat
PROVIDER_PRESETS = {
    "groq": {
        "api": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "needs_key": True,
    },
    "gemini": {
        "api": "openai",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.0-flash",
        "needs_key": True,
    },
    "openrouter": {
        "api": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "needs_key": True,
    },
    "ollama": {
        "api": "ollama",
        "base_url": "http://localhost:11434",
        "model": "llama3.1",
        "needs_key": False,
    },
    "openai": {
        "api": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "needs_key": True,
    },
    "anthropic": {
        "api": "anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-sonnet-5",
        "needs_key": True,
    },
}

REQUEST_TIMEOUT = 90


class AIProductDescriptionService(models.AbstractModel):
    _name = "ai.product.description.service"
    _description = "AI Product Description Generation Service"

    def _get_config(self):
        icp = self.env["ir.config_parameter"].sudo()
        provider = icp.get_param("ai_product_description.provider", "groq")
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["groq"])
        base_url = icp.get_param("ai_product_description.base_url") or preset["base_url"]
        try:
            temperature = float(icp.get_param("ai_product_description.temperature") or 0.7)
        except (TypeError, ValueError):
            temperature = 0.7
        return {
            "provider": provider,
            "api": preset["api"],
            "needs_key": preset["needs_key"],
            "api_key": icp.get_param("ai_product_description.api_key") or "",
            "base_url": base_url.rstrip("/"),
            "model": icp.get_param("ai_product_description.model") or preset["model"],
            "temperature": temperature,
        }

    def generate(self, system_prompt, user_prompt):
        """Return AI-generated text for the given prompts, or raise UserError."""
        cfg = self._get_config()
        if cfg["needs_key"] and not cfg["api_key"]:
            raise UserError(_(
                "No API key set for the selected AI provider.\n"
                "Go to Settings → AI Product Description and paste your key "
                "(Groq, Gemini and OpenRouter all offer free keys)."
            ))
        try:
            if cfg["api"] == "anthropic":
                return self._call_anthropic(cfg, system_prompt, user_prompt)
            if cfg["api"] == "ollama":
                return self._call_ollama(cfg, system_prompt, user_prompt)
            return self._call_openai(cfg, system_prompt, user_prompt)
        except requests.exceptions.Timeout:
            raise UserError(_("The AI provider took too long to respond. Please try again."))
        except requests.exceptions.RequestException as err:
            _logger.warning("AI Product Description request failed: %s", err)
            raise UserError(_("Could not reach the AI provider:\n%s") % err)
        except (KeyError, IndexError, ValueError) as err:
            _logger.warning("Unexpected AI provider response: %s", err)
            raise UserError(_("The AI provider returned an unexpected response. Please try again."))

    def _call_openai(self, cfg, system_prompt, user_prompt):
        response = requests.post(
            "%s/chat/completions" % cfg["base_url"],
            headers={
                "Authorization": "Bearer %s" % cfg["api_key"],
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "temperature": cfg["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=REQUEST_TIMEOUT,
        )
        self._raise_for_api_error(response)
        return response.json()["choices"][0]["message"]["content"].strip()

    def _call_anthropic(self, cfg, system_prompt, user_prompt):
        response = requests.post(
            "%s/messages" % cfg["base_url"],
            headers={
                "x-api-key": cfg["api_key"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "max_tokens": 1024,
                "temperature": cfg["temperature"],
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=REQUEST_TIMEOUT,
        )
        self._raise_for_api_error(response)
        return response.json()["content"][0]["text"].strip()

    def _call_ollama(self, cfg, system_prompt, user_prompt):
        response = requests.post(
            "%s/api/chat" % cfg["base_url"],
            json={
                "model": cfg["model"],
                "stream": False,
                "options": {"temperature": cfg["temperature"]},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=REQUEST_TIMEOUT,
        )
        self._raise_for_api_error(response)
        return response.json()["message"]["content"].strip()

    def _raise_for_api_error(self, response):
        if response.status_code >= 400:
            detail = response.text
            try:
                payload = response.json()
                if isinstance(payload, dict):
                    err = payload.get("error", payload)
                    detail = err.get("message", detail) if isinstance(err, dict) else str(err)
            except ValueError:
                pass
            raise UserError(_("AI provider error (%(code)s):\n%(detail)s") % {
                "code": response.status_code,
                "detail": detail,
            })
