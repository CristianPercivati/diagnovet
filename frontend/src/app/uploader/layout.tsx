import Header from "@/components/header";
import Footer from "@/components/footer";
import { ReactNode } from "react";


export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="screen dashboard-screen">
      <Header />
      
      <div className="main-content">
        
        {children}

      </div>

    </div>
  );
}
