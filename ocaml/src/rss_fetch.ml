open Lwt.Infix

let http_get url =
  let uri = Uri.of_string url in
  Cohttp_lwt_unix.Client.get uri >>= fun (resp, body) ->
  let status = Cohttp.Response.status resp in
  match Cohttp.Code.code_of_status status with
  | 200 -> Cohttp_lwt.Body.to_string body >|= fun s -> Ok s
  | c -> Lwt.return (Error (Printf.sprintf "HTTP %d for %s" c url))

(* Placeholder simplistic RSS item extraction (real implementation should parse XML) *)
let extract_items (_xml : string) : Article.t list =
  []

let fetch_feed feed =
  http_get feed.Config.url >|= function
  | Ok body ->
      let items = extract_items body in
      Ok items
  | Error e -> Error e

let fetch_all feeds =
  Lwt_list.map_p fetch_feed feeds >|= fun results ->
  let articles, errors =
    List.fold_left
      (fun (acc_ok, acc_err) -> function
        | Ok lst -> (lst @ acc_ok, acc_err)
        | Error e -> (acc_ok, e :: acc_err))
      ([], []) results
  in
  (List.rev articles, List.rev errors)
