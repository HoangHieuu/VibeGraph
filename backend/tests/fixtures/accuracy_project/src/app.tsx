import { Button } from "./components/Button";

export default function App({ user }: { user: { name: string } }) {
  return <Button label={user.name} />;
}
