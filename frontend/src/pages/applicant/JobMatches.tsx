import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, MapPin, Clock, IndianRupee, Bookmark, Send, Loader2, BookmarkCheck } from "lucide-react";
import axios from "axios";

export default function ApplicantJobMatches() {
  const userId = localStorage.getItem("user_id");

  const [jobs, setJobs] = useState<any[]>([]);
  const [bookmarkedIds, setBookmarkedIds] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [locationFilter, setLocationFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all-types");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/jobs");
        setJobs(res.data.jobs || []);
      } catch (err) {
        console.error("Failed to fetch jobs", err);
      }

      if (userId) {
        try {
          const bmRes = await axios.get(`http://127.0.0.1:5000/api/bookmarks?applicant_id=${userId}`);
          setBookmarkedIds(bmRes.data.bookmarked_job_ids || []);
        } catch (err) {
          console.error("Failed to fetch bookmarks", err);
        }
      }

      setLoading(false);
    };
    fetchData();
  }, [userId]);

  const toggleBookmark = async (jobId: string) => {
    if (!userId) return;
    try {
      if (bookmarkedIds.includes(jobId)) {
        await axios.delete(`http://127.0.0.1:5000/api/bookmarks/by-job?applicant_id=${userId}&job_id=${jobId}`);
        setBookmarkedIds(bookmarkedIds.filter(id => id !== jobId));
      } else {
        await axios.post("http://127.0.0.1:5000/api/bookmarks", { applicant_id: userId, job_id: jobId });
        setBookmarkedIds([...bookmarkedIds, jobId]);
      }
    } catch (err) {
      console.error("Failed to toggle bookmark", err);
    }
  };

  const handleApply = async (jobId: string) => {
    if (!userId) {
      alert("Please log in to apply.");
      return;
    }
    const hasResume = jobs.find(j => j.job_id === jobId);
    if (hasResume) {
      window.open(`mailto:?subject=Job Application&body=I'm interested in applying for this position.`, "_blank");
    }
  };

  const filteredJobs = jobs.filter(j => {
    const matchesSearch = j.title?.toLowerCase().includes(search.toLowerCase()) || j.recruiter_name?.toLowerCase().includes(search.toLowerCase());
    return matchesSearch;
  });

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
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Job Matches</h1>
        <p className="text-slate-500 mt-1">Opportunities ranked by how well they match your extracted skills.</p>
      </div>

      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search roles or companies..." 
            className="pl-9 bg-slate-50 border-slate-200"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <Select value={locationFilter} onValueChange={setLocationFilter}>
            <SelectTrigger className="w-[140px] bg-slate-50">
              <SelectValue placeholder="Location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Locations</SelectItem>
              <SelectItem value="remote">Remote</SelectItem>
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[140px] bg-slate-50">
              <SelectValue placeholder="Job Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all-types">All Types</SelectItem>
              <SelectItem value="full">Full-time</SelectItem>
              <SelectItem value="contract">Contract</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredJobs.length === 0 ? (
          <div className="col-span-2 p-12 text-center text-slate-500">
            No jobs found. Check back later for new opportunities.
          </div>
        ) : filteredJobs.map((job, i) => (
          <Card key={job.job_id} className="hover:shadow-md transition-shadow duration-300 animate-in fade-in zoom-in-95" style={{ animationDelay: `${i * 50}ms`, animationFillMode: 'both' }}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-600 text-lg">
                    {(job.recruiter_name || "C").charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-slate-900">{job.title}</h3>
                    <p className="text-slate-600 text-sm">{job.recruiter_name || "Company"}</p>
                  </div>
                </div>
                <Badge className="bg-slate-100 text-slate-700 hover:bg-slate-100 border-none px-3 py-1 text-sm font-bold">
                  Pending
                </Badge>
              </div>

              <div className="flex flex-wrap gap-3 mb-4">
                <div className="flex items-center text-xs text-slate-500 gap-1 bg-slate-50 px-2 py-1 rounded-md">
                  <MapPin className="h-3 w-3" /> Remote
                </div>
                <div className="flex items-center text-xs text-slate-500 gap-1 bg-slate-50 px-2 py-1 rounded-md">
                  <Clock className="h-3 w-3" /> Full-time
                </div>
                <div className="flex items-center text-xs text-slate-500 gap-1 bg-slate-50 px-2 py-1 rounded-md">
                  <IndianRupee className="h-3 w-3" /> Negotiable
                </div>
              </div>

              <div className="mb-6">
                <p className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-2">Required Skills</p>
                <div className="flex flex-wrap gap-2">
                  {job.skills?.length > 0 ? job.skills.map((skill: string) => (
                    <Badge key={skill} variant="secondary" className="bg-slate-100 text-slate-600 font-normal">
                      {skill}
                    </Badge>
                  )) : (
                    <span className="text-xs text-slate-400">No skills listed</span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                <span className="text-xs text-slate-400">
                  {job.created_at ? new Date(job.created_at).toLocaleDateString() : "Recently"}
                </span>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon" className="text-slate-400 hover:text-slate-900" onClick={() => toggleBookmark(job.job_id)}>
                    {bookmarkedIds.includes(job.job_id) ? (
                      <BookmarkCheck className="h-4 w-4 text-[#F97316]" />
                    ) : (
                      <Bookmark className="h-4 w-4" />
                    )}
                  </Button>
                  <Button className="bg-[#F97316] hover:bg-[#F97316]/90 text-white gap-2" onClick={() => handleApply(job.job_id)}>
                    <Send className="h-4 w-4" /> Apply Now
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
