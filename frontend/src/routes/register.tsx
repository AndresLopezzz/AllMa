import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import type { FormEvent } from "react";
import { useState } from "react";
import { register } from "@/lib/api/services/auth";
import { useAuthStore } from "@/lib/store/AuthStore";
import { toast } from "sonner";
import logo from "@/assets/logo.svg";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from "@/components/ui";

const PLAN_OPTIONS = [
  { label: "Plan gratuito (Free)", value: "free" },
  { label: "Plan profesional (Pro)", value: "pro" },
] as const;

type PlanValue = (typeof PLAN_OPTIONS)[number]["value"];

export const Route = createFileRoute("/register")({
  beforeLoad: () => {
    const authStore = useAuthStore.getState();
    authStore.initializeAuth();

    if (authStore.isAuthenticated()) {
      throw redirect({ to: "/dashboard" });
    }
  },
  component: Register,
});

function Register() {
  const [name, setName] = useState("");
  const [plan, setPlan] = useState<PlanValue>("free");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const setUser = useAuthStore((state) => state.setUser);
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (password !== password2) {
      toast.error("Las contraseñas no coinciden.");
      return;
    }

    try {
      setLoading(true);

      const data = await register({
        email,
        password,
        password2,
        name,
        plan,
      });

      setUser(data.user, { access: data.access, refresh: data.refresh });
      toast.success("Registro exitoso");
      navigate({ to: "/dashboard" });
    } catch (err) {
      toast.error(
        "No pudimos crear tu cuenta. Verifica los datos e inténtalo nuevamente.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background text-foreground p-6">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img src={logo} alt="AllMa" className="h-8 w-auto dark:invert" />
          </div>
          <CardTitle>Crear una cuenta</CardTitle>
          <CardDescription>
            Regístrate para comenzar a gestionar tus inventarios.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="name">Nombre completo</Label>
              <Input
                id="name"
                type="text"
                placeholder="Tu nombre"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="email">Correo electrónico</Label>
              <Input
                id="email"
                type="email"
                placeholder="tu@email.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="plan">Selecciona tu plan</Label>
              <select
                id="plan"
                className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none focus:border-ring focus-visible:ring-ring/50"
                value={plan}
                onChange={(event) => {
                  const value = event.target.value as PlanValue;
                  setPlan(value);
                }}
              >
                {PLAN_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="password2">Confirmar contraseña</Label>
              <Input
                id="password2"
                type="password"
                placeholder="Repite tu contraseña"
                value={password2}
                onChange={(event) => setPassword2(event.target.value)}
                required
              />
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creando cuenta..." : "Registrarme"}
            </Button>

            <p className="text-center text-sm text-muted-foreground">
              ¿Ya tienes cuenta?{" "}
              <a
                href="/login"
                className="text-primary underline-offset-4 hover:underline"
              >
                Inicia sesión
              </a>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
