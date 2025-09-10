let translate ~api_key ~text ~target_lang =
  if target_lang = "pl" then Lwt.return (Ok text)
  else (
    let _headers = Cohttp.Header.init_with "Authorization" ("Bearer " ^ api_key) in
    (* Placeholder: perform OpenRouter API call; return original for now *)
    Lwt.return (Ok text)
  )
