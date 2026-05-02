import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Building2, LogOut, Briefcase, X } from "lucide-react";

interface Company {
  name: string;
  industry: string;
  description: string;
  requiredSkills: string[];
}

export default function RecruiterDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(() => {
    const stored = localStorage.getItem('company');
    return stored ? JSON.parse(stored) : null;
  });
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    description: '',
  });
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState<string[]>([]);

  useEffect(() => {
    if (!user || user.role !== 'recruiter') {
      navigate('/');
    }
  }, [user, navigate]);

  const handleAddSkill = () => {
    if (skillInput.trim() && !skills.includes(skillInput.trim())) {
      setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setSkills(skills.filter(s => s !== skill));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newCompany: Company = {
      ...formData,
      requiredSkills: skills,
    };
    setCompany(newCompany);
    localStorage.setItem('company', JSON.stringify(newCompany));
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (company) {
    return (
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-md border-b-4 border-emerald-500">
          <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
            <div className="flex items-center gap-3 text-gray-800">
              <Building2 className="w-7 h-7 text-emerald-600" />
              <span className="text-2xl">{company.name}</span>
            </div>
            <Button variant="outline" onClick={handleLogout} className="h-10 px-6">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-6">
            <h1 className="text-3xl mb-2">Recruiter Dashboard</h1>
            <p className="text-gray-600">Manage your job postings and find candidates</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Company Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Company Name</Label>
                  <p>{company.name}</p>
                </div>
                <div>
                  <Label>Industry</Label>
                  <p>{company.industry}</p>
                </div>
                <div>
                  <Label>Description</Label>
                  <p className="text-sm text-gray-600">{company.description}</p>
                </div>
                <div>
                  <Label>Required Skills</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {company.requiredSkills.map((skill) => (
                      <Badge key={skill} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
                <Button variant="outline" onClick={() => setCompany(null)}>
                  Edit Company
                </Button>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-xl transition-all transform hover:scale-105 border-gray-200 shadow-md" onClick={() => navigate('/recruiter/jobs')}>
              <CardHeader>
                <div className="w-14 h-14 bg-emerald-100 rounded-lg flex items-center justify-center mb-3">
                  <Briefcase className="w-7 h-7 text-emerald-600" />
                </div>
                <CardTitle>Job Postings</CardTitle>
                <CardDescription>Create and manage job openings</CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full bg-emerald-500 hover:bg-emerald-600">Manage Jobs</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-md border-b-4 border-emerald-500">
        <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
          <div className="flex items-center gap-3 text-gray-800">
            <Building2 className="w-7 h-7 text-emerald-600" />
            <span className="text-2xl">SipSetu</span>
          </div>
          <Button variant="outline" onClick={handleLogout} className="h-10 px-6">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Register Your Company</CardTitle>
            <CardDescription>
              Provide your company details and specify the skills you're looking for
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Company Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Company Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="skills">Required Skills</Label>
                <div className="flex gap-2">
                  <Input
                    id="skills"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    placeholder="e.g., React, Python, Leadership"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                  />
                  <Button type="button" onClick={handleAddSkill}>Add</Button>
                </div>
                {skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="pl-3 pr-1">
                        {skill}
                        <button
                          type="button"
                          onClick={() => handleRemoveSkill(skill)}
                          className="ml-2 hover:bg-gray-300 rounded-full p-0.5"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={skills.length === 0}>
                Register Company
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
