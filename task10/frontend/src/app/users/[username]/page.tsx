import { notFound } from "next/navigation";

interface Post {
  id: string;
  text: string;
  timestamp: string;
  owner_id: string;
  owner_username: string;
}

interface Props {
  params: { username: string };
}

export default async function UserProfilePage({ params }: Props) {
  const { username } = params;
  let posts: Post[] = [];
  let error = null;

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/users/${username}/posts`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("User not found or error fetching posts");
    posts = await res.json();
  } catch (e: any) {
    error = e.message;
  }

  if (error) {
    notFound();
  }

  return (
    <main style={{ maxWidth: 600, margin: "2rem auto" }}>
      <h1>Профиль пользователя: {username}</h1>
      <h2>Посты:</h2>
      {posts.length === 0 ? (
        <p>У пользователя пока нет постов.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {posts.map((post) => (
            <li key={post.id} style={{ border: "1px solid #ccc", borderRadius: 8, margin: "1rem 0", padding: 16 }}>
              <div>{post.text}</div>
              <div style={{ fontSize: 12, color: "#888" }}>{new Date(post.timestamp).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
} 