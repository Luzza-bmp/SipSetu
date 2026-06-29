import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FileText, Download, UploadCloud, Edit3, Sparkles, Loader2, X, Check, Plus } from "lucide-react";
import axios from "axios";
import { useNavigate } from "react-router";

export default function ApplicantResume() {
  const navigate = useNavigate();
  const userId = localStorage.getItem("user_id");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [resume, setResume] = useState<any>(null);
  const [skills, setSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editSkills, setEditSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    fetchResume();
  }, []);

  const fetchResume = async () => {
    if (!userId) { setLoading(false); return; }
    try {
      const res = await axios.get(`http://127.0.0.1:5000/api/resumes?applicant_id=${userId}`);
      if (res.data.length > 0) {
        const latest = res.data[0];
        setResume(latest);
        setSkills(latest.skills || []);
      }
    } catch (err) {
      console.error("Failed to fetch resume", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!userId) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("applicant_id", userId);
      const res = await axios.post("http://127.0.0.1:5000/api/resumes/upload", formData);
      await fetchResume();
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload resume. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
  };

  const handleDownload = () => {
    if (!resume?.resume_id) return;
    window.open(`http://127.0.0.1:5000/api/uploads/${resume.resume_id}`, "_blank");
  };

  const toggleEdit = () => {
    if (editing) {
      setSkills(editSkills);
      setEditing(false);
    } else {
      setEditSkills([...skills]);
      setEditing(true);
    }
  };

  const addEditSkill = () => {
    if (newSkill.trim() && !editSkills.includes(newSkill.trim())) {
      setEditSkills([...editSkills, newSkill.trim()]);
      setNewSkill("");
    }
  };

  const removeEditSkill = (skill: string) => {
    setEditSkills(editSkills.filter(s => s !== skill));
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">My Resume</h1>
        <p className="text-slate-500 mt-1">Manage your document and extracted skills profile.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Current Document</CardTitle>
              <CardDescription>Your active resume used for matching.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {resume ? (
                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-start gap-4">
                  <div className="h-12 w-12 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                    <FileText className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-slate-900 truncate">Resume #{resume.resume_id?.substring(0, 8)}</h4>
                    <p className="text-sm text-slate-500 mt-1">
                      Uploaded {resume.uploaded_at ? new Date(resume.uploaded_at).toLocaleDateString() : "Recently"} • {skills.length} skills extracted
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" className="flex-shrink-0 text-slate-400 hover:text-slate-900" onClick={handleDownload}>
                    <Download className="h-5 w-5" />
                  </Button>
                </div>
              ) : (
                <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 text-center">
                  <p className="text-slate-500">No resume uploaded yet.</p>
                </div>
              )}

              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf,.docx"
                className="hidden"
              />
              <div
                className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer ${
                  dragOver ? "border-[#1E3A5F] bg-blue-50" : "border-slate-200 bg-slate-50/50 hover:bg-slate-50"
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
              >
                {uploading ? (
                  <Loader2 className="h-8 w-8 animate-spin text-[#1E3A5F] mb-4" />
                ) : (
                  <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <UploadCloud className="h-6 w-6 text-[#1E3A5F]" />
                  </div>
                )}
                <h4 className="font-semibold text-slate-900">{uploading ? "Uploading..." : resume ? "Replace Resume" : "Upload Resume"}</h4>
                <p className="text-sm text-slate-500 mt-1 max-w-xs">
                  {uploading ? "Please wait while we process your file..." : "Drag and drop a PDF or DOCX, or click to browse."}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-100 shadow-sm">
            <CardContent className="p-6 flex items-start gap-4">
              <div className="h-10 w-10 rounded-full bg-white shadow-sm flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h4 className="font-bold text-indigo-900 mb-1">Build a resume with AI</h4>
                <p className="text-sm text-indigo-700/80 mb-4">Don't have a solid resume yet? Use our AI builder to craft one tailored for tech roles.</p>
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm" onClick={() => window.open("https://docs.google.com", "_blank")}>
                  Start Building
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-8">
          <Card className="h-full flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-100">
              <div>
                <CardTitle>Extracted Profile</CardTitle>
                <CardDescription>What our AI found in your document.</CardDescription>
              </div>
              <Button variant="outline" size="sm" className="gap-2" onClick={toggleEdit}>
                {editing ? <><Check className="h-4 w-4" /> Done</> : <><Edit3 className="h-4 w-4" /> Edit</>}
              </Button>
            </CardHeader>
            <CardContent className="pt-6 flex-1">
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-3">Verified Skills</h4>
                  {editing ? (
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        {editSkills.map((skill) => (
                          <Badge key={skill} className="bg-[#1E3A5F] text-white px-3 py-1 gap-1">
                            {skill}
                            <X className="h-3 w-3 cursor-pointer" onClick={() => removeEditSkill(skill)} />
                          </Badge>
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <Input
                          value={newSkill}
                          onChange={(e) => setNewSkill(e.target.value)}
                          placeholder="Add a skill..."
                          className="h-9 text-sm"
                          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addEditSkill(); } }}
                        />
                        <Button size="sm" variant="outline" className="h-9" onClick={addEditSkill}>
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {skills.length === 0 ? (
                        <p className="text-sm text-slate-400">Upload a resume to extract skills.</p>
                      ) : skills.map((skill, i) => (
                        <Badge key={skill} className={i < 4 ? "bg-[#1E3A5F] hover:bg-[#1E3A5F]/90 text-white px-3 py-1" : "bg-slate-100 text-slate-700 hover:bg-slate-200 px-3 py-1"}>
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-6 border-t border-slate-100">
                  <h4 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-3">Experience Summary</h4>
                  <p className="text-slate-600 text-sm leading-relaxed">
                    {skills.length > 0
                      ? `Frontend developer with expertise in ${skills.slice(0, 4).join(", ")}. Demonstrated ability to build modern, responsive web applications with a focus on user experience and performance.`
                      : "Upload your resume to see an AI-generated experience summary based on your extracted skills and work history."}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
