import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { ArrowLeft } from "lucide-react";

export default function Login() {
  const { role } = useParams<{ role: 'applicant' | 'recruiter' }>();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (role) {
      await login(email, password, role);
      navigate(role === 'recruiter' ? '/recruiter/dashboard' : '/applicant/dashboard');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-200 p-8 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1/4 h-full bg-emerald-500" style={{ clipPath: 'polygon(0 0, 100% 0, 40% 100%, 0% 100%)' }}></div>
      <div className="absolute top-0 right-0 w-1/4 h-full bg-emerald-500" style={{ clipPath: 'polygon(60% 0, 100% 0, 100% 100%, 100% 100%)' }}></div>

      <Card className="w-full max-w-lg bg-white shadow-2xl relative z-10">
        <CardHeader className="p-8">
          <Button
            variant="ghost"
            className="w-fit mb-4 -ml-2"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <CardTitle className="text-4xl mb-3">
            Login Account
          </CardTitle>
          <CardDescription className="text-base">
            Enter your credentials to continue
          </CardDescription>
        </CardHeader>
        <CardContent className="p-8 pt-0">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-base">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 text-base"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-base">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-12 text-base"
              />
            </div>
            <Button type="submit" className="w-full h-12 text-base bg-emerald-500 hover:bg-emerald-600 text-white">
              Login Account
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
