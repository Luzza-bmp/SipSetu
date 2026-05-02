import { useNavigate } from "react-router";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Briefcase, User } from "lucide-react";

export default function RoleSelection() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-200 p-8 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1/4 h-full bg-emerald-500" style={{ clipPath: 'polygon(0 0, 100% 0, 40% 100%, 0% 100%)' }}></div>
      <div className="absolute top-0 right-0 w-1/4 h-full bg-emerald-500" style={{ clipPath: 'polygon(60% 0, 100% 0, 100% 100%, 100% 100%)' }}></div>

      <div className="w-full max-w-6xl relative z-10">
        <div className="text-center mb-16">
          <h1 className="text-7xl mb-6 text-gray-800 tracking-wide">SipSetu</h1>
          <p className="text-2xl text-gray-600">No Skills Left Behind</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-4xl mx-auto px-8">
          <Card
            className="cursor-pointer hover:shadow-2xl transition-all duration-300 bg-white border-0 transform hover:scale-105 shadow-lg"
            onClick={() => navigate('/login/applicant')}
          >
            <CardHeader className="text-center py-16">
              <div className="mx-auto w-28 h-28 bg-emerald-100 rounded-full flex items-center justify-center mb-6">
                <User className="w-14 h-14 text-emerald-600" />
              </div>
              <CardTitle className="text-3xl text-gray-800">Applicant</CardTitle>
            </CardHeader>
            <CardContent className="pb-12">
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer hover:shadow-2xl transition-all duration-300 bg-white border-0 transform hover:scale-105 shadow-lg"
            onClick={() => navigate('/login/recruiter')}
          >
            <CardHeader className="text-center py-16">
              <div className="mx-auto w-28 h-28 bg-emerald-100 rounded-full flex items-center justify-center mb-6">
                <Briefcase className="w-14 h-14 text-emerald-600" />
              </div>
              <CardTitle className="text-3xl text-gray-800">Recruiter</CardTitle>
            </CardHeader>
            <CardContent className="pb-12">
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
