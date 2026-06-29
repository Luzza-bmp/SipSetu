import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ExternalLink, Target, CheckCircle2, ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import axios from "axios";
import { useNavigate } from "react-router";

const defaultResources: Record<string, string[]> = {
  "typescript": ["https://www.typescriptlang.org/docs/", "https://www.udemy.com/course/understanding-typescript/", "https://frontendmasters.com/courses/typescript-v3/"],
  "node.js": ["https://nodejs.org/en/docs/", "https://www.theodinproject.com/paths/full-stack-javascript", "https://www.udemy.com/course/nodejs-complete-guide/"],
  "system design": ["https://github.com/donnemartin/system-design-primer", "https://www.youtube.com/playlist?list=PLTCrU9sGyburBw9wNOHebv9SjlW4w8sNq"],
  "testing": ["https://jestjs.io/docs/getting-started", "https://testing-library.com/docs/"],
  "python": ["https://docs.python.org/3/", "https://www.codecademy.com/learn/learn-python-3"],
  "react": ["https://react.dev/", "https://reacttraining.com/"],
  "css": ["https://developer.mozilla.org/en-US/docs/Web/CSS", "https://css-tricks.com/"],
  "docker": ["https://docs.docker.com/", "https://www.udemy.com/course/docker-mastery/"],
  "aws": ["https://aws.amazon.com/training/", "https://acloudguru.com/"],
  "sql": ["https://www.w3schools.com/sql/", "https://sqlbolt.com/"],
};

export default function ApplicantSkillGap() {
  const navigate = useNavigate();
  const userId = localStorage.getItem("user_id");

  const [matchedJobs, setMatchedJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({});
  const [readiness, setReadiness] = useState(0);
  const [strengths, setStrengths] = useState<string[]>([]);
  const [missingSkills, setMissingSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) { setLoading(false); return; }
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/jobs`);
        const jobs = res.data.jobs || [];
        setMatchedJobs(jobs);
        if (jobs.length > 0) {
          setSelectedJob(jobs[0].job_id);
          analyzeSkills(jobs[0]);
        }

        const statsRes = await axios.get(`http://127.0.0.1:5000/api/applicants/${userId}/stats`);
        setReadiness(statsRes.data.match_score || 0);
      } catch (err) {
        console.error("Failed to fetch data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userId]);

  const analyzeSkills = async (job: any) => {
    try {
      const resSkills = await axios.get(`http://127.0.0.1:5000/api/resumes?applicant_id=${userId}`);
      const allResumeSkills: string[] = resSkills.data.length > 0 ? resSkills.data[0].skills || [] : [];

      const jobSkills: string[] = (job.skills || []).map((s: string) => s.toLowerCase());
      const missing = jobSkills.filter((s: string) => !allResumeSkills.map((rs: string) => rs.toLowerCase()).includes(s));
      const present = allResumeSkills.filter((s: string) => jobSkills.includes(s.toLowerCase()));

      const missingWithPriority = missing.map((s: string) => ({
        skill: s.charAt(0).toUpperCase() + s.slice(1),
        priority: jobSkills.indexOf(s) < jobSkills.length / 3 ? "High" : jobSkills.indexOf(s) < jobSkills.length * 2 / 3 ? "Medium" : "Low",
      }));

      setMissingSkills(missingWithPriority);
      setStrengths(present);
      if (missingWithPriority.length > 0) {
        setOpenItems({ [missingWithPriority[0].skill]: true });
      }

      const score = jobSkills.length > 0 ? Math.round((present.length / jobSkills.length) * 100) : 0;
      setReadiness(score);
    } catch (err) {
      console.error("Failed to analyze skills", err);
    }
  };

  const handleJobChange = (value: string) => {
    setSelectedJob(value);
    const job = matchedJobs.find(j => j.job_id === value);
    if (job) analyzeSkills(job);
  };

  const toggleItem = (skill: string) => {
    setOpenItems(prev => ({ ...prev, [skill]: !prev[skill] }));
  };

  const getResourceUrls = (skill: string): string[] => {
    const key = skill.toLowerCase();
    return defaultResources[key] || [
      `https://www.google.com/search?q=learn+${encodeURIComponent(skill)}+online`,
      `https://www.youtube.com/results?search_query=${encodeURIComponent(skill)}+tutorial`,
      `https://www.udemy.com/courses/search/?q=${encodeURIComponent(skill)}`,
    ];
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#1E3A5F]" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Skill Gap Analysis</h1>
          <p className="text-slate-500 mt-1">See exactly what's standing between you and your target roles.</p>
        </div>
        <div className="w-full md:w-80">
          <p className="text-sm font-medium text-slate-700 mb-2">Analyze skill gap for:</p>
          <Select value={selectedJob} onValueChange={handleJobChange}>
            <SelectTrigger className="bg-white border-slate-200">
              <SelectValue placeholder="Select a job" />
            </SelectTrigger>
            <SelectContent>
              {matchedJobs.map(job => (
                <SelectItem key={job.job_id} value={job.job_id}>{job.title} @ {job.recruiter_name || "Company"}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-t-4 border-t-[#F97316]">
            <CardHeader>
              <CardTitle className="text-xl">Missing Skills to Learn</CardTitle>
              <CardDescription>
                {missingSkills.length > 0
                  ? `We've identified ${missingSkills.length} critical skills required for this role that aren't in your profile.`
                  : "Great match! No critical skill gaps detected for this role."}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {missingSkills.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">No missing skills for this role!</div>
                ) : missingSkills.map((item) => (
                  <Collapsible 
                    key={item.skill} 
                    open={openItems[item.skill]} 
                    onOpenChange={() => toggleItem(item.skill)}
                    className="p-4 bg-white"
                  >
                    <CollapsibleTrigger className="w-full flex items-center justify-between group">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${
                          item.priority === 'High' ? 'bg-red-50 text-red-600' :
                          item.priority === 'Medium' ? 'bg-orange-50 text-orange-600' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          <Target className="h-4 w-4" />
                        </div>
                        <span className="font-semibold text-slate-900">{item.skill}</span>
                        <Badge variant="outline" className={
                          item.priority === 'High' ? 'border-red-200 text-red-700 bg-red-50' :
                          item.priority === 'Medium' ? 'border-orange-200 text-orange-700 bg-orange-50' :
                          'border-slate-200 text-slate-700 bg-slate-50'
                        }>
                          {item.priority} Priority
                        </Badge>
                      </div>
                      <Button variant="ghost" size="sm" className="text-slate-400 group-hover:text-slate-900">
                        {openItems[item.skill] ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </Button>
                    </CollapsibleTrigger>
                    
                    <CollapsibleContent className="pt-4 pl-14">
                      <p className="text-sm font-medium text-slate-900 mb-3 uppercase tracking-wider">Recommended Resources</p>
                      <ul className="space-y-2">
                        {getResourceUrls(item.skill).map((url, i) => (
                          <li key={i}>
                            <a 
                              href={url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-sm text-[#1E3A5F] hover:underline gap-1.5 p-1.5 -ml-1.5 rounded hover:bg-blue-50 transition-colors"
                            >
                              <ExternalLink className="h-3.5 w-3.5 text-slate-400" />
                              {url.split('/')[2] || url}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </CollapsibleContent>
                  </Collapsible>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-[#1E3A5F] text-white border-none shadow-lg">
            <CardContent className="p-8 text-center">
              <div className="relative w-32 h-32 mx-auto mb-6">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" className="text-white/20 stroke-current" strokeWidth="8" fill="none" />
                  <circle cx="50" cy="50" r="40" className="text-[#F97316] stroke-current" strokeWidth="8" fill="none" strokeDasharray="251.2" strokeDashoffset={251.2 - (251.2 * readiness) / 100} strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center flex-col">
                  <span className="text-4xl font-bold">{readiness}<span className="text-xl">%</span></span>
                </div>
              </div>
              <h3 className="text-xl font-bold mb-2">Role Readiness</h3>
              <p className="text-blue-100 text-sm mb-6">
                {readiness >= 70
                  ? "You have a strong foundation for this role! Addressing the gaps will make you a top candidate."
                  : readiness >= 40
                  ? "You have a decent start. Focus on high-priority gaps to improve your chances."
                  : "This role may require significant upskilling. Start with the high-priority items."}
              </p>
              <Button className="w-full bg-[#F97316] hover:bg-[#F97316]/90 text-white border-none" onClick={() => navigate("/applicant/resume")}>
                Boost Your Profile
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">Your Strengths</CardTitle>
              <CardDescription>Matching skills you already possess.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {strengths.length === 0 ? (
                  <p className="text-sm text-slate-400">No matching skills found for this role.</p>
                ) : strengths.map(skill => (
                  <Badge key={skill} className="bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 px-3 py-1 font-medium gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    {skill}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
