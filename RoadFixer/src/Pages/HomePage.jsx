import Banner from "../components/Banner";
import Stats from "../components/Stats";
import Features from "../components/Features";
import RecentAccidents from "../components/DataCollection";

export default function HomePage() {
  return (
    <main style={{ backgroundColor: 'var(--preto)' }}>
      <Banner />
      <Stats />
      <Features />
      <RecentAccidents />
    </main>
  );
}