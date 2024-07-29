import Link from "next/link";

export default function Docs() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">API Docs Page</h1>
      <p className="text-lg mb-8">This is the API documentation page.</p>
      <Link href="/" className="text-blue-500 hover:underline">
        Go back to Home
      </Link>
    </main>
  );
}
