module Yaml = Yaml

type feed = { name : string; url : string } [@@deriving yojson]
type t = {
  feeds : feed list;
  max_articles : int;
  email_to : string;
  email_from : string;
} [@@deriving yojson]


let load_file path : (t, string) result =
  match Yaml_unix.of_file Fpath.(v path) with
  | Ok (`O assoc) -> (
      (* Very small hand extraction; refine later *)
      let get k = List.assoc_opt k assoc in
      let feeds =
        match get "feeds" with
        | Some (`A lst) ->
            List.filter_map
              (function
                | `O kv -> (
                    match (List.assoc_opt "name" kv, List.assoc_opt "url" kv) with
                    | Some (`String n), Some (`String u) ->
                        Some { name = n; url = u }
                    | _ -> None )
                | _ -> None)
              lst
        | _ -> []
      in
      let int_field k default =
        match get k with Some (`Float f) -> int_of_float f | _ -> default
      in
      let string_field k default =
        match get k with Some (`String s) -> s | _ -> default
      in
      Ok
        {
          feeds;
          max_articles = int_field "max_articles" 100;
          email_to = string_field "email_to" "";
          email_from = string_field "email_from" "";
        })
  | Ok _ -> Error "Unexpected YAML structure"
  | Error (`Msg e) -> Error e

let require_env name =
  match Sys.getenv_opt name with
  | Some v when v <> "" -> Ok v
  | _ -> Error (Printf.sprintf "Missing required env var %s" name)
