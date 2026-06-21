import App from "@/app";
import type { User } from "@/types";
import * as utils from "@/utils";

export { helper as renamed } from "@/helpers";

export const start = (user: User) => App({ user, utils });
