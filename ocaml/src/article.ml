(* Provide yojson converters for Ptime.t via an alias so ppx_deriving_yojson
   can pick up ptime_to_yojson / ptime_of_yojson automatically. *)
type ptime = Ptime.t

let ptime_to_yojson (t : ptime) = `String (Ptime.to_rfc3339 t)

let ptime_of_yojson = function
  | `String s -> (
      match Ptime.of_rfc3339 s with
      | Ok (t, _, _) -> Ok t
      | Error _ -> Error "ptime_of_yojson: invalid RFC3339 timestamp")
  | _ -> Error "ptime_of_yojson: expected string"

type t = {
  id : string;
  title : string;
  url : string;
  published : ptime option [@yojson.option];
  source : string;
  language : string;  (* ISO code, e.g. "pl", "en" *)
  content : string;   (* Raw / extracted text *)
} [@@deriving yojson]

let create ?published ~id ~title ~url ~source ~language ~content () =
  { id; title; url; published; source; language; content }

let is_recent ~since t =
  match (t.published, since) with
  | Some p, Some threshold -> Ptime.is_later ~than:threshold p
  | _, None -> true
  | None, Some _ -> true (* keep if unknown date *)

let to_brief t =
  Printf.sprintf "%s (%s)" t.title t.source
