class Formatter:
    def _format_tokens(tokens: list = None) -> list[str]:
        if tokens is None: tokens = []
        formatted_tokens = []
        for token in tokens:
            if ":" in token:
                token = token.split(":")[-1]  # email:pass:token
            formatted_tokens.append(token)
        return formatted_tokens

    def _format_proxies(proxies: list = []) -> list[str]:
        return proxies  # idk yet

    def _format_roles(roles: list[dict] = [], blacklisted: list[str] = []) -> list[str]:
        formatted_roles = []
        for role in roles:
            if role.get("id") not in blacklisted:
                formatted_roles.append(role.get("name"))
        return formatted_roles
