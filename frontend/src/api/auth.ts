import request from "./client";
import type { UserPublic, Token } from "./types";

async function register(email: string, password: string) {
  const call = await request<UserPublic>({
    path: "/register",
    method: "POST",
    body: { email: email, password: password },
  });
  return call;
}
async function login(email: string, password: string) {
  const call = await request<Token>({
    path: "/login",
    method: "POST",
    body: { email: email, password: password },
  });
  return call;
}

export { register, login };
