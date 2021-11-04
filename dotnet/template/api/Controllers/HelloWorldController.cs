using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

/*
Please delete this file.
*/

namespace HelloWorldController
{
    [ApiController]
    [Route("hello-world")]
    public class HelloWorldController : ControllerBase
    {
        [HttpGet]
        public string Get()
        {
            return "This is your newly created Auctane Platform Service running! Congratulations! 🎉🎉";
        }
    }
}
