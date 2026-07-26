interface UserPublic {
  readonly id: number;
  readonly email: string;
}
interface Token {
  readonly access_token: string;
  readonly token_type: string;
}

export type { Token, UserPublic };
