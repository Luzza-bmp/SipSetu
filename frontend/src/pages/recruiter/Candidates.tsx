import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Search, MapPin, Briefcase, ChevronDown, FileText, Mail, Loader2 } from "lucide-react";
import axios from "axios";

export default function RecruiterCandidates() {
  const userId = localStorage.getItem("user_id");

  const [candidates, setCandidates] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [jobFilter, setJobFilter] = useState("all-jobs");
  const [statusFilter, setStatusFilter] = useState("all-status");
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) { setLoading(false); return; }
    const fetchCandidates = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/recruiters/${userId}/candidates`);
        setCandidates(res.data.candidates || []);
      } catch (err) {
        console.error("Failed to fetch candidates", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, [userId]);

  const updateStatus = async (rankingId: string, newRank: number | null) => {
    setUpdatingId(rankingId);
    try {
      await axios.put(`http://127.0.0.1:5000/api/rankings/${rankingId}`, { candidate_rank: newRank });
      setCandidates(candidates.map(c => 
        c.ranking_id === rankingId ? { ...c, candidate_rank: newRank } : c
      ));
    } catch (err) {
      console.error("Failed to update status", err);
    } finally {
      setUpdatingId(null);
    }
  };

  const getStatusFromRank = (rank: number | null): string => {
    if (rank === null || rank === undefined) return "Applied";
    if (rank <= 3) return "Shortlisted";
    if (rank <= 6) return "In Review";
    return "Rejected";
  };

  const getStatusBadge = (rank: number | null) => {
    const status = getStatusFromRank(rank);
    switch (status) {
      case 'Shortlisted': return <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none">Shortlisted</Badge>;
      case 'In Review': return <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-100 border-none">In Review</Badge>;
      case 'Rejected': return <Badge className="bg-red-100 text-red-700 hover:bg-red-100 border-none">Rejected</Badge>;
      default: return <Badge className="bg-slate-100 text-slate-700 hover:bg-slate-100 border-none">Applied</Badge>;
    }
  };

  const uniqueJobs = [...new Set(candidates.map(c => c.job_title).filter(Boolean))];

  const filteredCandidates = candidates.filter(c => {
    const name = (c.applicant_name || "").toLowerCase();
    const skills = (c.resume_skills || []).join(" ").toLowerCase();
    const matchesSearch = name.includes(search.toLowerCase()) || skills.includes(search.toLowerCase());
    const matchesJob = jobFilter === "all-jobs" || c.job_title === jobFilter;
    const matchesStatus = statusFilter === "all-status" || getStatusFromRank(c.candidate_rank).toLowerCase() === statusFilter;
    return matchesSearch && matchesJob && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#F97316]" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Ranked Candidates</h1>
        <p className="text-slate-500 mt-1">Applicants automatically scored and ranked against your job requirements.</p>
      </div>

      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search candidates or skills..." 
            className="pl-9 bg-slate-50 border-slate-200"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <Select value={jobFilter} onValueChange={setJobFilter}>
            <SelectTrigger className="w-[180px] bg-slate-50">
              <SelectValue placeholder="Filter by Job" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all-jobs">All Postings</SelectItem>
              {uniqueJobs.map(job => (
                <SelectItem key={job} value={job}>{job}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px] bg-slate-50">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all-status">Any Status</SelectItem>
              <SelectItem value="applied">Applied</SelectItem>
              <SelectItem value="in review">In Review</SelectItem>
              <SelectItem value="shortlisted">Shortlisted</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        {filteredCandidates.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            No candidates found. Post a job to start receiving applications.
          </div>
        ) : filteredCandidates.map((candidate, i) => (
          <Card key={candidate.ranking_id || i} className="overflow-hidden hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-2" style={{ animationDelay: `${i * 50}ms` }}>
            <CardContent className="p-0">
              <div className="flex flex-col md:flex-row items-stretch">
                <div className="flex md:flex-col items-center justify-between md:justify-center md:w-32 p-4 md:p-6 bg-slate-50 border-b md:border-b-0 md:border-r border-slate-100 shrink-0">
                  <div className="text-sm font-bold text-slate-400 mb-1">RANK #{i + 1}</div>
                  <div className={`text-3xl font-extrabold ${(candidate.matching_score || 0) >= 85 ? 'text-green-600' : (candidate.matching_score || 0) >= 70 ? 'text-orange-500' : 'text-slate-600'}`}>
                    {Math.round(candidate.matching_score || 0)}<span className="text-base">%</span>
                  </div>
                  <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mt-1">Match</div>
                </div>

                <div className="flex-1 p-4 md:p-6 flex flex-col justify-center">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
                    <div className="flex items-center gap-4">
                      <Avatar className="h-12 w-12 border border-slate-200">
                        <AvatarFallback className="bg-[#1E3A5F] text-white font-semibold">
                          {(candidate.applicant_name || "?").split(' ').map((n: string) => n[0]).join('').substring(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-bold text-lg text-slate-900">{candidate.applicant_name || "Unknown"}</h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500 mt-1">
                          <span className="flex items-center gap-1"><Briefcase className="h-3.5 w-3.5" /> {candidate.job_title || "Applicant"}</span>
                          {candidate.applicant_location && (
                            <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {candidate.applicant_location}</span>
                          )}
                          <span className="flex items-center gap-1 text-[#1E3A5F] font-medium">{(candidate.resume_skills?.length || 0)} skills</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between md:justify-end md:w-auto gap-3">
                      {getStatusBadge(candidate.candidate_rank)}
                    </div>
                  </div>

                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-auto">
                    <div className="flex flex-wrap gap-2">
                      {(candidate.resume_skills || []).slice(0, 5).map((skill: string) => (
                        <Badge key={skill} variant="secondary" className="bg-slate-100 text-slate-700 font-normal border border-slate-200/50">
                          {skill}
                        </Badge>
                      ))}
                      {(candidate.resume_skills?.length || 0) > 5 && (
                        <Badge variant="secondary" className="bg-slate-100 text-slate-400 font-normal">
                          +{candidate.resume_skills.length - 5} more
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2 shrink-0">
                      {candidate.applicant_email && (
                        <a href={`mailto:${candidate.applicant_email}`}>
                          <Button variant="outline" size="icon" className="h-9 w-9 text-slate-500 border-slate-200" title="Email Candidate">
                            <Mail className="h-4 w-4" />
                          </Button>
                        </a>
                      )}
                      <Button className="h-9 bg-[#1E3A5F] hover:bg-[#1E3A5F]/90 text-white gap-2" onClick={() => alert("Resume view coming soon!")}>
                        <FileText className="h-4 w-4" /> View Resume
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" className="h-9 gap-1 text-slate-700 border-slate-200" disabled={updatingId === candidate.ranking_id}>
                            {updatingId === candidate.ranking_id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <>Status <ChevronDown className="h-4 w-4" /></>
                            )}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => updateStatus(candidate.ranking_id, 10)} className="text-slate-700">Mark as Applied</DropdownMenuItem>
                          <DropdownMenuItem onClick={() => updateStatus(candidate.ranking_id, 5)} className="text-blue-600 font-medium">Move to Review</DropdownMenuItem>
                          <DropdownMenuItem onClick={() => updateStatus(candidate.ranking_id, 1)} className="text-green-600 font-medium">Shortlist</DropdownMenuItem>
                          <DropdownMenuItem onClick={() => updateStatus(candidate.ranking_id, 20)} className="text-red-600">Reject</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
