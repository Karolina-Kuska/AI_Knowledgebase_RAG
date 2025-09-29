using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using System.Text;
using System.IdentityModel.Tokens.Jwt;
using Microsoft.IdentityModel.Tokens;

namespace WebApp.Chat.Controllers
{
    [ApiController]
    [Route("aspapi/auth")]
    public class AuthController : ControllerBase
    {
    
        private readonly IConfiguration _config;

        public AuthController(IConfiguration config)
        {
            _config = config;
        }

        [HttpPost("login")]
        public IActionResult Login([FromBody] LoginRequest req)
        {
          
            var validUsername = _config["Auth:Username"];
            var validPassword = _config["Auth:Password"];

            if (req.Username != validUsername || req.Password != validPassword)
                return Unauthorized("Invalid username or password.");

            var claims = new[]
            {
                  new Claim(ClaimTypes.Name, req.Username)
            };

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["JwtKey"] ?? "kkZTFQYM7icE76jKjAQd3hlr9G1Kx8ak"));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var token = new JwtSecurityToken(
                issuer: _config["JwtIssuer"] ?? "WebApp.Chat",
                audience: null,
                claims: claims,
                expires: DateTime.Now.AddHours(12),
                signingCredentials: creds);

            var jwt = new JwtSecurityTokenHandler().WriteToken(token);

            return Ok(new { token = jwt });
        }

        public class LoginRequest
        {
            public string Username { get; set; } = string.Empty;
            public string Password { get; set; } = string.Empty;
        }
    }
}
