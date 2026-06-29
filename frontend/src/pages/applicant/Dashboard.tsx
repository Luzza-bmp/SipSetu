import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Target, FileText, Briefcase, Eye, ChevronRight, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router";
import { useState, useEffect } from "react";
import axios from "axios";

export default function ApplicantDashboardHome() {
  const navigate = useNavigate();
  const date = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  const userName = localStorage.getItem("user_name") || "User";
  const userId = localStorage.getItem("user_id");

  const [jobs, setJobs] = useState<any[]>([]);
  const [stats, setStats] = useState({
    match_score: 0,
    resume_strength: 0,
    jobs_applied: 0,
    profile_views: 0,
    skill_gaps: [] as string[],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const jobsRes = await axios.get("http://localhost:5000/api/jobs");
        setJobs(jobsRes.data.jobs || []);
      } catch (err) {
        console.error("Failed to fetch jobs", err);
      }

      if (userId) {
        try {
          const statsRes = await axios.get(`http://127.0.0.1:5000/api/applicants/${userId}/stats`);
          setStats(statsRes.data);
        } catch (err) {
          console.error("Failed to fetch stats", err);
        }
      }

      setLoading(false);
    };
    fetchData();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#1E3A5F]" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Welcome back, {userName} 👋</h1>
        <p className="text-slate-500 mt-1">{date}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-500">Avg. Match Score</p>
              <p className="text-3xl font-bold text-[#F97316]">{stats.match_score}%</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-orange-50 flex items-center justify-center">
              <Target className="h-6 w-6 text-[#F97316]" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col justify-center space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Resume Strength</p>
              <FileText className="h-5 w-5 text-blue-500" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-bold text-slate-900">{stats.resume_strength}/100</span>
              </div>
              <Progress value={stats.resume_strength} className="h-2 bg-slate-100" indicatorClassName="bg-[#1E3A5F]" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-500">Jobs Applied</p>
              <p className="text-3xl font-bold text-slate-900">{stats.jobs_applied}</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center">
              <Briefcase className="h-6 w-6 text-slate-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-500">Profile Views</p>
              <p className="text-3xl font-bold text-slate-900">{stats.profile_views}</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center">
              <Eye className="h-6 w-6 text-slate-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-100">
            <CardTitle className="text-lg font-bold">Top Job Matches</CardTitle>
            <Link to="/applicant/matches">
              <Button variant="ghost" size="sm" className="text-slate-500 hover:text-[#1E3A5F]">
                View All <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="p-0 flex-1">
            <div className="divide-y divide-slate-100">
              {jobs.length === 0 ? (
                <div className="p-8 text-center text-slate-500">No jobs posted yet. Check back later!</div>
              ) : jobs.slice(0, 4).map((job) => (
                <div key={job.job_id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="space-y-1">
                    <h3 className="font-semibold text-slate-900">{job.title}</h3>
                    <p className="text-sm text-slate-500">{(job.recruiter_name || "Recruiter")} • {job.skills?.length || 0} skills</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {job.skills && job.skills.map((skill: string) => (
                        <span key={skill} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{skill}</span>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge className={'bg-slate-100 text-slate-700 hover:bg-slate-100'}>
                      Pending Analysis
                    </Badge>
                    <Button variant="outline" size="sm" onClick={() => navigate(`/applicant/matches?job=${job.job_id}`)}>View</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-8">
          <Card>
            <CardHeader className="pb-2 border-b border-slate-100">
              <CardTitle className="text-lg font-bold">Critical Skill Gaps</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-6 space-y-6">
              <p className="text-sm text-slate-600">Top missing skills for roles you're matching with:</p>
              <div className="flex flex-wrap gap-2">
                {stats.skill_gaps.length === 0 ? (
                  <p className="text-sm text-slate-400">No skill gaps identified yet.</p>
                ) : stats.skill_gaps.map(skill => (
                  <Badge key={skill} variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-200">
                    {skill}
                  </Badge>
                ))}
              </div>
              <Link to="/applicant/skill-gap">
                <Button variant="outline" className="w-full text-[#1E3A5F] border-[#1E3A5F]/20 hover:bg-blue-50">
                  View Full Analysis
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2 border-b border-slate-100">
              <CardTitle className="text-lg font-bold">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-6">
              <div className="space-y-4">
                {stats.jobs_applied > 0 ? (
                  <div className="flex gap-3 items-start">
                    <div className="h-8 w-8 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Briefcase className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{stats.jobs_applied} job{stats.jobs_applied > 1 ? 's' : ''} applied</p>
                      <p className="text-xs text-slate-500">Across all your matched positions</p>
                    </div>
                  </div>
                ) : null}
                {stats.resume_strength > 0 ? (
                  <div className="flex gap-3 items-start">
                    <div className="h-8 w-8 rounded-full bg-orange-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <FileText className="h-4 w-4 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">Resume uploaded</p>
                      <p className="text-xs text-slate-500">Strength: {stats.resume_strength}/100</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex gap-3 items-start">
                    <div className="h-8 w-8 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Target className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">Get started</p>
                      <p className="text-xs text-slate-500">Upload your resume to see matches</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
