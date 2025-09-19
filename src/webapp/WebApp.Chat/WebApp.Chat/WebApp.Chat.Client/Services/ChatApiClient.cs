using System.Net.Http.Json;

namespace WebApp.Chat.Client.Services;

public record ChatRequest(string session_id, string message);
public record SourceItem(string? title, string? source, string? preview);
public record ChatResponse(string answer, string intent, string? engine, List<SourceItem> sources);

public class ChatApiClient
{
    private readonly HttpClient _http;
    public ChatApiClient(HttpClient http) => _http = http;

    public async Task<ChatResponse?> SendAsync(string sessionId, string message, CancellationToken ct = default)
    {
        var payload = new ChatRequest(sessionId, message);
        using var resp = await _http.PostAsJsonAsync("/chat", payload, ct);
        resp.EnsureSuccessStatusCode();
        return await resp.Content.ReadFromJsonAsync<ChatResponse>(cancellationToken: ct);
    }

    public async Task ClearAsync(string sessionId, CancellationToken ct = default)
    {
        using var resp = await _http.PostAsJsonAsync("/chat/clear", new { session_id = sessionId }, ct);
        resp.EnsureSuccessStatusCode();
    }
}
