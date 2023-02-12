def api_helper(form, subject):
    api_req = {
        subject: form["slots"].get(subject, {}).get("value"),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    return api_req
