import GalleryGrid from "../components/GalleryGrid";

export default function Gallery() {
  return (
    <div className="p-8 fade-up max-w-[1600px] mx-auto">
      <div className="mb-5">
        <h1 className="text-2xl font-semibold tracking-tight">Gallery</h1>
        <p className="text-sm text-ink-400 mt-1">Everything you've created. Hover videos to preview.</p>
      </div>
      <GalleryGrid />
    </div>
  );
}
